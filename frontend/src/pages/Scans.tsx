import { Link } from 'react-router-dom'; // Importa Link

function Scans() {

  return (
    // Container principal: tela cheia, fundo com imagem, e display flex para dividir em colunas.
    <div
      className="min-h-screen bg-cover bg-center flex"
      style={{ backgroundImage: "url('/assets/fundo.png')" }} // Fundo azul com imagem
    >
      {/* Sidebar AZUL à esquerda (1/5 da largura da tela) com a cor #15688f */}
      {/* Usando inline style para a cor hexadecimal exata */}
      <div
        className="w-1/5 #15688f text-white flex flex-col items-center justify-center p-4 shadow-lg min-h-screen"
      >
        <Link to="/">
          <img
            src="/assets/logocogel.jpg" // Caminho da nova logo da COGEL
            alt="COGEL Logo"
            className="w-32 h-auto mb-4" // Ajuste o tamanho da logo e margem
          />
        </Link>
        {/* Adicione outros links ou conteúdo para a sidebar aqui, se necessário */}
      </div>

      {/* Conteúdo central (área BRANCA à direita, 4/5 da largura da tela) */}
      <div className="w-4/5 bg-white flex items-center justify-center p-8 min-h-screen">
        <div className="grid grid-cols-3 gap-10 text-center">
          {/* Botão Web Application Scans */}
          <Link to="/pesquisar-scan-was"> {/* Link atualizado para o endpoint correto */}
            <div className="hover:scale-105 transition cursor-pointer">
              <img
                src="/assets/web.png" // Ícone para Web App Scans
                alt="Web Application Scans"
                className="mx-auto h-25 mb-4" // h-25 é um bom tamanho, ajuste se necessário
              />
              <p className="text-black font-medium text-lg">Web Application Scans</p>
            </div>
          </Link>

          {/* Botão Vulnerability Management Scans */}
          <Link to="/pesquisar-scan-vm"> {/* Link atualizado para o endpoint correto */}
            <div className="hover:scale-105 transition cursor-pointer">
              <img
                src="/assets/vm.png" // Ícone para VM Scans
                alt="Vulnerability Management Scans"
                className="mx-auto h-25 mb-4"
              />
              <p className="text-black font-medium text-lg">Vulnerability Management Scans</p>
            </div>
          </Link>

          {/* Botão Listas de Scans */}
          <Link to='/lista-de-scans'>
            <div className="hover:scale-105 transition cursor-pointer">
              <img
                src="/assets/listas.png" // Ícone para Listas de Scans
                alt="Listas de Scans"
                className="mx-auto h-25 mb-4"
              />
              <p className="text-black font-medium text-lg">Listas de Scans</p>
            </div>
          </Link>
        </div>
      </div>
    </div>
  );
}

export default Scans;