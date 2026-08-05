import urllib.request
import json
import re
import os

USER = 'georgeofilho'

CONFIG = [
    {
        'topic': 'sysadmin',
        'start_marker': '<!-- START_SYSADMIN_REPOS -->',
        'end_marker': '<!-- END_SYSADMIN_REPOS -->'
    },
    {
        'topic': 'zabbix-templates',
        'start_marker': '<!-- START_ZABBIX_TEMPLATES_REPOS -->',
        'end_marker': '<!-- END_ZABBIX_TEMPLATES_REPOS -->'
    },
    {
        'topic': 'zabbix-module',
        'start_marker': '<!-- START_ZABBIX_MODULES_REPOS -->',
        'end_marker': '<!-- END_ZABBIX_MODULES_REPOS -->'
    }
]

def fetch_repos(topic):
    url = f'https://api.github.com/search/repositories?q=user:{USER}+topic:{topic}'
    req = urllib.request.Request(url)
    req.add_header('Accept', 'application/vnd.github.v3+json')
    
    # Adicionar token se disponível para evitar limite de requisições do GitHub (Rate Limit)
    token = os.getenv('GITHUB_TOKEN')
    if token:
        req.add_header('Authorization', f'token {token}')

    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
        return data.get('items', [])
    except Exception as e:
        print(f"Erro ao buscar repositórios para o tópico {topic}: {e}")
        return []

def generate_markdown_list(repos, topic):
    if not repos:
        return f"  - _Nenhum repositório com a tag {topic} encontrado no momento._\n"

    # Ordena os repositórios pela data de atualização (mais recentes primeiro)
    repos.sort(key=lambda x: x['updated_at'], reverse=True)
    markdown_list = ""
    for repo in repos:
        name = repo['name']
        url = repo['html_url']
        desc = repo.get('description') or 'Sem descrição'
        markdown_list += f"  - [{name}]({url}) - {desc}\n"
    return markdown_list

def update_readme():
    with open('README.md', 'r', encoding='utf-8') as f:
        readme = f.read()

    for item in CONFIG:
        topic = item['topic']
        start = item['start_marker']
        end = item['end_marker']
        
        repos = fetch_repos(topic)
        markdown_list = generate_markdown_list(repos, topic)
        
        # Regex para encontrar a área entre os comentários e substituir pela nova lista
        pattern = rf"({start}\n).*?(\s*{end})"
        readme = re.sub(pattern, rf"\g<1>{markdown_list}\g<2>", readme, flags=re.DOTALL)

    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme)

if __name__ == "__main__":
    update_readme()
    print("README.md atualizado com sucesso para todas as tags!")
