update_docs_workflow_content = """
name: Start Actions on Commit for Updating Documentation
on:
  pull_request:
    branches:
      - '**'
  
jobs:          
  documentation:
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    environment: GPT
    permissions:
      contents: write
    steps:
      - name: Checkout Code
        uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with: 
         python-version: '3.10'

      - name: Set up .env file
        run: |
          echo "GLOBAL_LLM_SERVICE=${GLOBAL_LLM_SERVICE}" >> .env
          echo "CHAT_DEPLOYMENT_NAME=${CHAT_DEPLOYMENT_NAME}" >> .env
          echo "AZURE_OPENAI_API_KEY=${AZURE_OPENAI_API_KEY}" >> .env
          echo "AZURE_OPENAI_ENDPOINT=${AZURE_OPENAI_ENDPOINT}" >> .env
          echo "AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME=${AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME}" >> .env
          echo "AZURE_OPENAI_API_VERSION=${AZURE_OPENAI_API_VERSION}" >> .env
          echo "AZURE_AI_SEARCH_KEY=${AZURE_AI_SEARCH_KEY}" >> .env
          echo "API_TYPE=${API_TYPE}" >> .env
          echo "BASE_URL=${BASE_URL}" >> .env
          echo "SEARCH_ENDPOINT=${SEARCH_ENDPOINT}" >> .env
          echo "GITHUB_ACCESS_TOKEN=${GITHUB_ACCESS_TOKEN}" >> .env
        shell: bash
        env:
          GLOBAL_LLM_SERVICE: ${{ secrets.GLOBAL_LLM_SERVICE }}
          CHAT_DEPLOYMENT_NAME: ${{ secrets.CHAT_DEPLOYMENT_NAME }}
          AZURE_OPENAI_API_KEY: ${{ secrets.AZURE_OPENAI_API_KEY }}
          AZURE_OPENAI_ENDPOINT: ${{ secrets.AZURE_OPENAI_ENDPOINT }}
          AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME: ${{ secrets.AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME }}
          AZURE_OPENAI_API_VERSION: ${{ secrets.AZURE_OPENAI_API_VERSION }}
          AZURE_AI_SEARCH_KEY: ${{ secrets.AZURE_AI_SEARCH_KEY }}
          API_TYPE: ${{ secrets.API_TYPE }}
          BASE_URL: ${{ secrets.BASE_URL }}
          SEARCH_ENDPOINT: ${{ secrets.SEARCH_ENDPOINT }}
          GITHUB_ACCESS_TOKEN: ${{ secrets.GITHUB_ACCESS_TOKEN }}

      - name: Get local branches
        run: |
          git fetch origin main
          git checkout main
          git fetch origin ${{ github.head_ref }}
          git checkout ${{ github.head_ref }}

      - name: Run Docker Compose
        run: docker-compose up --build --detach
        env: 
          name: gpt
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        
      - name: Set safe.directory in repo-copilot container
        run: docker exec repo-copilot git config --global --add safe.directory /workspace

      - name: Run update documentation script
        run: |
          docker exec repo-copilot python3 /repo-copilot/repo_documentation/update_app.py --branch "${{ github.head_ref }}"

      - name: Commit and push if changes in repository
        run: |
          git config --local user.email "github-actions@github.com"
          git config --local user.name "github-actions"
          git add .
          git diff-index --quiet HEAD || (git commit -m "Documentation Updated" && git pull --rebase)
          git push
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
"""

update_comments_workflow_content = """
name: Update Documentation on Pull Request Comment

on: 
  issue_comment:
    types: [created]

jobs:
  pr_comment:
    runs-on: ubuntu-latest
    environment: GPT
    permissions:
      contents: write 
    name: PR comment
    if: ${{ github.event.issue.pull_request }} && startsWith(github.event.comment.body, 'Documentation ')

    steps:
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'

      - name: Get PR branch
        uses: xt0rted/pull-request-comment-branch@v1
        id: comment-branch

      - name: Checkout PR branch
        uses: actions/checkout@v3
        with:
          ref: ${{ steps.comment-branch.outputs.head_ref }}

      - name: Get file path name and comment
        id: extract
        run: |
          COMMENT="${{ github.event.comment.body }}"
          FILE_PATH=$(echo "$COMMENT" | grep -oP '(?<=Documentation\s)[^:]*' | awk '{print $1}')
          COMMENT_BODY=$(echo "$COMMENT" | sed -E 's/^Documentation [^ ]* //')
          echo "file_path=$FILE_PATH" >> $GITHUB_OUTPUT
          echo "comment_body=$COMMENT_BODY" >> $GITHUB_OUTPUT

      - name: Set up .env file
        run: |
          echo "GLOBAL_LLM_SERVICE=${GLOBAL_LLM_SERVICE}" >> .env
          echo "CHAT_DEPLOYMENT_NAME=${CHAT_DEPLOYMENT_NAME}" >> .env
          echo "AZURE_OPENAI_API_KEY=${AZURE_OPENAI_API_KEY}" >> .env
          echo "AZURE_OPENAI_ENDPOINT=${AZURE_OPENAI_ENDPOINT}" >> .env
          echo "AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME=${AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME}" >> .env
          echo "AZURE_OPENAI_API_VERSION=${AZURE_OPENAI_API_VERSION}" >> .env
          echo "AZURE_AI_SEARCH_KEY=${AZURE_AI_SEARCH_KEY}" >> .env
          echo "API_TYPE=${API_TYPE}" >> .env
          echo "BASE_URL=${BASE_URL}" >> .env
          echo "SEARCH_ENDPOINT=${SEARCH_ENDPOINT}" >> .env
          echo "GITHUB_ACCESS_TOKEN=${GITHUB_ACCESS_TOKEN}" >> .env
        shell: bash
        env:
          GLOBAL_LLM_SERVICE: ${{ secrets.GLOBAL_LLM_SERVICE }}
          CHAT_DEPLOYMENT_NAME: ${{ secrets.CHAT_DEPLOYMENT_NAME }}
          AZURE_OPENAI_API_KEY: ${{ secrets.AZURE_OPENAI_API_KEY }}
          AZURE_OPENAI_ENDPOINT: ${{ secrets.AZURE_OPENAI_ENDPOINT }}
          AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME: ${{ secrets.AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME }}
          AZURE_OPENAI_API_VERSION: ${{ secrets.AZURE_OPENAI_API_VERSION }}
          AZURE_AI_SEARCH_KEY: ${{ secrets.AZURE_AI_SEARCH_KEY }}
          API_TYPE: ${{ secrets.API_TYPE }}
          BASE_URL: ${{ secrets.BASE_URL }}
          SEARCH_ENDPOINT: ${{ secrets.SEARCH_ENDPOINT }}
          GITHUB_ACCESS_TOKEN: ${{ secrets.GITHUB_ACCESS_TOKEN }}

      - name: Run Docker Compose
        run: docker-compose up --build --detach
        env: 
          name: gpt
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        
      - name: Set safe.directory in repo-copilot container
        run: docker exec repo-copilot git config --global --add safe.directory /workspace

      - name: Update Documentation
        run: |
          git fetch origin ${{ steps.comment-branch.outputs.head_ref }}
          git checkout ${{ steps.comment-branch.outputs.head_ref }}
          docker exec repo-copilot python3 /repo-copilot/repo_documentation/update_app.py --branch "${{ steps.comment-branch.outputs.head_ref }}" --file "/workspace/$FILE_PATH" --comment "$COMMENT_BODY"
        env:
          FILE_PATH: ${{ steps.extract.outputs.file_path }}
          COMMENT_BODY: ${{ steps.extract.outputs.comment_body }}

      - name: Commit and push changes
        run: |
          git config --local user.email "github-actions@github.com"
          git config --local user.name "github-actions"
          git add -A
          git diff-index --quiet HEAD || (git commit -m "Update documentation for ${{ steps.extract.outputs.file_path }}" && git pull --rebase)
          git push
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
"""