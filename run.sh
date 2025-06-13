#!/bin/bash
# Define cores para melhor visualização no terminal
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Iniciando a Aplicação AudiTex Docker  ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Verifica se o Docker está rodando
if ! docker info > /dev/null 2>&1; then
  echo -e "${RED}Erro: O Docker não está rodando. Por favor, inicie o Docker e tente novamente.${NC}"
  exit 1
fi

echo -e "${GREEN}Docker está em execução. Prosseguindo...${NC}"
echo ""

# Navega para o diretório AudiTex antes de executar docker-compose
# Esta linha é necessária se você executar o script de um nível acima (e.g., de ~/ )
# Se você for executar o script DE DENTRO de ~/AudiTex, COMENTE a linha abaixo.
# cd AudiTex || { echo -e "${RED}Erro: Não foi possível entrar no diretório AudiTex. Verifique se ele existe.${NC}"; exit 1; }

# Constrói as imagens e sobe os contêineres em modo detached
echo -e "${YELLOW}Construindo as imagens e subindo os contêineres...${NC}"
docker-compose up -d --build

# Verifica se os contêineres foram iniciados com sucesso
if [ $? -eq 0 ]; then
  echo -e "${GREEN}Aplicação iniciada com sucesso!${NC}"
  echo ""
  echo -e "${BLUE}Status dos contêineres:${NC}"
  docker-compose ps
  echo ""
  echo -e "${GREEN}Sua aplicação frontend deve estar disponível em: http://localhost:3000${NC}"
  echo -e "${GREEN}Seu backend deve estar disponível em: http://localhost:5000${NC}"
  echo ""
  echo -e "${YELLOW}Para ver os logs em tempo real, execute: ${NC}docker-compose logs -f"
  echo -e "${YELLOW}Para parar a aplicação, execute: ${NC}docker-compose down -v"
else
  echo -e "${RED}Erro: Falha ao iniciar a aplicação. Verifique os logs acima para detalhes.${NC}"
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Processo de Inicialização Concluído   ${NC}"
echo -e "${BLUE}========================================${NC}"