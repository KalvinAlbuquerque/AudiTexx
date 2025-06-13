import { Link, useNavigate } from 'react-router-dom';

function Relatorios() {
  const navigate = useNavigate();

  return (
    // Container principal: tela cheia, fundo com imagem, e display flex para dividir em colunas.
    <div
      className="min-h-screen bg-cover bg-center flex" // 'flex' aqui para criar as duas colunas
      style={{ backgroundImage: "url('/assets/fundo.png')" }} // Fundo azul com imagem
    >
      {/* Sidebar AZUL CLARO à esquerda (1/5 da largura da tela) */}
      {/* Esta div tem uma cor de fundo sólida (bg-blue-600) que fica sobre a imagem de fundo. */}
      <div className="w-1/5 #15688f text-white flex flex-col items-center justify-center p-4 shadow-lg min-h-screen">
        <Link to="/">
          <img
            src="/assets/logocogel.jpg" // Caminho da nova logo da COGEL
            alt="COGEL Logo"
            className="w-32 h-auto mb-4" // Ajuste o tamanho da logo
          />
        </Link>
        {/* Adicione outros links ou conteúdo para a sidebar aqui, se necessário */}
      </div>

      {/* Conteúdo central (área BRANCA à direita, 4/5 da largura da tela) */}
      {/* Esta div tem um fundo branco sólido (bg-white) que cobre a imagem de fundo. */}
      <div className="w-4/5 bg-white flex items-center justify-center p-8 min-h-screen">
        <div className="grid grid-cols-2 gap-20 text-center">
          {/* Botão Relatórios Gerados */}
          <div
            className="hover:scale-105 transition cursor-pointer"
            onClick={() => navigate('/relatorios-gerados')}
          >
            <img
              src="/assets/gerados.png"
              alt="Relatórios Gerados"
              className="mx-auto h-30 mb-4"
            />
            <p className="text-black font-medium text-lg">Relatórios Gerados</p>
          </div>

          {/* Botão Gerar Relatórios */}
          <div
            className="hover:scale-105 transition cursor-pointer"
            onClick={() => navigate('/lista-de-scans')} // Aponta para a lista de scans para gerar relatório
          >
            <img
              src="/assets/gerar.png"
              alt="Gerar Relatórios"
              className="mx-auto h-30 mb-4"
            />
            <p className="text-black font-medium text-lg">Gerar Relatórios</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Relatorios;