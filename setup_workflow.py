import os

workflow_content = """
name: Start Actions on Commit for Generating and Updating Documentation
on:
  push:
      branches:
        - '**'
  
jobs:          
  documentation:
    if: github.event_name == 'push'
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - name: Checkout Code
        uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with: 
         python-version: '3.10'
      
      - name: Start ollama server
        run: curl -fsSL https://ollama.com/install.sh | sh
  
      - name: Run Llama 3
        run: ollama run llama3

      - name: Create workspace_data
        run: docker volume create workspace_data

      - name: Run docker image zenawang/repo-copilot:test
        run: docker run --rm -v $(pwd):/workspace -w /workspace -d --name repo-copilot zenawang/repo-copilot:test

      - name: Run generate/update documentation script
        run: |
          if [ -d "docs_output" ]; then
            docker exec repo-copilot python3 /repo-copilot/repo_documentation/app.py  
          else
            docker exec repo-copilot python3 /repo-copilot/repo_documentation/update_app.py "${{ github.ref_name }}"
          fi
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Commit and push if changes in repository
        run: |
          git checkout ${{ github.ref_name }}
          git config --local user.email "github-actions@github.com"
          git config --local user.name "github-actions"
          git add .
          git diff-index --quiet HEAD || (git commit -m "Documentation Updated" && git pull --rebase)
          git push
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
"""

def create_workflow():
    os.makedirs('/workspace/.github/workflows', exist_ok=True)
    with open('/workspace/.github/workflows/generate-update-docs.yml', 'w') as f:
        f.write(workflow_content)
        
if __name__ == "__main__":
    print("Creating workflow...")
    create_workflow()