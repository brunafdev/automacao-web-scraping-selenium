# 🕸️ Web Scraping & Data Mining (E-commerce)

> **Tecnologias:** Python, Selenium, BeautifulSoup, Pandas | **Status:** Concluído
> **Foco:** ETL, Tratamento de Erros e Extração em Larga Escala.

### O Cenário
A necessidade de monitorar preços e catálogo de produtos de concorrentes ou fornecedores exige automação. Fazer isso manualmente para milhares de SKUs é inviável.

### 💡 A Solução
Desenvolvi um **Crawler (Robô de Varredura)** robusto que navega autonomamente por todas as categorias de um e-commerce alvo.
Diferente de scripts simples, este robô possui **Auto-Healing**: se a conexão falhar ou o site bloquear, ele reinicia o navegador e retoma a extração sem perder os dados já coletados.

### ⚙️ Fluxo de Execução

```mermaid
graph TD
    A[🚀 Iniciar Driver] --> B[🗺️ Mapear Categorias]
    B --> C{Loop por Categoria}
    C -->|Acessar URL| D[📄 Extrair Produtos Pág. 1]
    D --> E{Tem Paginação?}
    E -- Sim --> F[🔄 Loop: Próximas Páginas]
    E -- Não --> G[💾 Armazenar em Memória]
    F --> G
    G --> H{Erro de Conexão?}
    H -- Sim --> I[🛠️ Reiniciar Driver e Tentar Novamente]
    I --> C
    H -- Não --> J[📊 Exportar Excel Final]
