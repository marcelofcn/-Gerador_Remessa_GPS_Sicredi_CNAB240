Crie um plano detalhado para desenvolver um frontend web simples e elegante para um script Python de automação de dados (Excel, PDF, e-mail).

CONTEXTO DO PROJETO:
- Nome do projeto: geraremessa
- Script Python: automacao_remessa.py
- Funcionalidades: Manipulação de dados Excel, leitura de PDFs, envio de e-mails
- Estrutura de pastas: app/ (raiz), INPUT_DIR (entrada), PROCESSED_DIR (saída), NSA_FILE (nomes)
- README: https://github.com/neviim/geraremessa

REQUISITOS DO FRONTEND:
1. Simples e elegante (sem frameworks como React/Vue/Next.js)
2. Tecnologias: HTML5 + CSS3 + JavaScript (ES6+)
3. Design limpo e profissional
4. Responsivo (funciona em desktop e mobile)
5. Acessível (boa contraste, fonts legíveis)

ESTRUTURA DO FRONTEND:
1. Página inicial (Dashboard)
   - Mostra resumo das funcionalidades
   - Botões de ação
   - Design moderno e clean

2. Página de Upload de Arquivos
   - Upload de arquivo Excel
   - Upload de arquivo PDF
   - Lista de arquivos carregados

3. Página de Configuração
   - Campos para INPUT_DIR, OUTPUT_DIR, PROCESSED_DIR, NSA_FILE
   - Botão "Salvar Configuração"
   - Validação de campos

4. Página de Execução
   - Botão "Executar Script"
   - Mostra progresso (simulado ou real via API)
   - Logs de execução
   - Mensagens de sucesso/erro

5. Página de Relatórios
   - Mostra dados do Excel processado
   - Gráficos simples (barras, linhas)
   - Tabelas de resultados
   - Botão para exportar (CSV, PDF)

DESIGN E UX:
- Cores: Palette moderna (azul, branco, cinza claro)
- Tipografia: Sans-serif (Inter, Roboto, Open Sans)
- Layout: Espaçado, com hierarchy visual
- Micro-interações: Hover effects, transições suaves
- Ícones: Use emojis ou SVG icons (FontAwesome sem dependências)

ARQUITETURA DE ARQUIVOS:
- index.html (página principal)
- styles.css (estilos globais)
- script.js (lógica JavaScript)
- assets/ (imagens, ícones se houver)
- templates/ (templates HTML para SPA simples)

FUNCIONALIDADES JAVASCRIPT:
- Navegação SPA simples (show/hide sections)
- Validação de formulários
- Upload de arquivos (simulado ou real via API)
- Fetch de dados (simulado ou real via API)
- Exibição de relatórios (simulado ou real)

PLANO DE IMPLEMENTAÇÃO:
1. Estrutura HTML básica
2. Design CSS (reset, layout, components)
3. Lógica JavaScript (navegação, interação)
4. Integração com Python (API REST simples ou mocks)
5. Testes e validação
6. Refinamento de design
7. Deploy (simulado ou real)

CONSIDERAÇÕES TÉCNICAS:
- Single Page Application (SPA) simples sem frameworks
- Uso de JavaScript Vanilla (sem React, Vue, etc.)
- Uso de CSS moderno (Grid, Flexbox, Variables)
- Uso de HTML semântico (header, nav, main, footer, article, section)
- Acessibilidade (aria-labels, focus styles, contrast)
- Performance (código otimizado, minificação opcional)

Por favor, forneça:
1. Estrutura detalhada do index.html
2. Estilos CSS principais (cores, fonts, layout)
3. Lógica JavaScript principal (navegação, interação)
4. Planos de seção para Dashboard, Upload, Configuração, Execução, Relatórios
5. Exemplos de código para HTML, CSS e JS
6. Sugestões de design e UX

Crie um plano completo e profissional.
