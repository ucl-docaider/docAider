import os
import subprocess

workflow_content = """
name: Start Actions on Commit for Updating Documentation
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

      - name: Install Graphviz
        run: sudo apt-get install -y graphviz
  
      - name: Run Llama 3
        run: ollama run llama3

      - name: Run update documentation script
        run: |
          cd repo_copilot/repo_documentation
          git checkout zena/test_doc_update
          python update_app.py "${{ github.ref_name }}"
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Commit and push if changes in clucker
        run: |
          git checkout ${{ github.ref_name }}
          git config --local user.email "github-actions@github.com"
          git config --local user.name "github-actions"
          git config remote.origin.url "https://github.com/ZenaWangqwq/clucker.git"
          git add .
          git diff-index --quiet HEAD || (git commit -m "Documentation Updated" && git pull --rebase)
          git push
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
"""

def create_workflow():
    # 创建 .github/workflows 目录
    os.makedirs('/workspace/.github/workflows', exist_ok=True)
    # 写入 workflow 文件
    with open('/workspace/.github/workflows/update-docs.yml', 'w') as f:
        f.write(workflow_content)
        
if __name__ == "__main__":
    print("Creating workflow...")
    create_workflow()