// init-mongo-app-user.js
// Este script cria o usuário 'admin' diretamente no banco de dados 'mydatabase'.
// Usamos db.getSiblingDB para garantir que o usuário seja criado no banco de dados correto,
// evitando o comando "use mydatabase;" que pode gerar avisos no editor.

db.getSiblingDB('mydatabase').createUser(
  {
    user: "admin",
    pwd: "admin", // A senha da sua aplicação
    roles: [
      { role: "readWrite", db: "mydatabase" } // Permissão de leitura e escrita para 'mydatabase'
    ]
  }
);