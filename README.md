# Sistema de Academia de Musculação

Sistema web para gerenciamento de uma academia de musculação, com áreas para administrador e aluno.

## Funcionalidades
- **Administrador**:
  - Login com usuário e senha (padrão: admin/admin).
  - Cadastro, edição e exclusão de alunos.
  - Cadastro, edição e exclusão de planos de treino com upload de foto.
  - Cadastro, edição e exclusão de mensalidades com geração de QR code para Pix.
  - Envio e recebimento de mensagens com alunos.
- **Aluno**:
  - Login com usuário e senha.
  - Visualização de perfil com dados completos.
  - Visualização de planos de treino.
  - Visualização de mensalidades com QR code para Pix.
  - Envio e recebimento de mensagens com o administrador.

## Instalação
1. Clone o repositório:
   ```bash
   git clone <URL_DO_REPOSITORIO>
   ```
2. Crie um ambiente virtual e instale as dependências:
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Crie o diretório `static/uploads` para armazenar fotos e QR codes.
4. Execute o aplicativo:
   ```bash
   python app.py
   ```
5. Acesse `http://localhost:5000` no navegador.

## Estrutura do Banco de Dados
- **users**: Armazena informações de usuários (admin e alunos).
- **workouts**: Armazena planos de treino com descrição e foto.
- **payments**: Armazena mensalidades com valor, vencimento, chave Pix e QR code.
- **messages**: Armazena mensagens entre admin e alunos.

## Notas
- As senhas são armazenadas com hash (bcrypt).
- Os QR codes para Pix são gerados automaticamente com base na chave Pix fornecida.
- Certifique-se de que o diretório `static/uploads` existe antes de executar o sistema.
