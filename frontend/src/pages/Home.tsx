import { useNavigate } from 'react-router-dom';

function Home() {
  const navigate = useNavigate();

  return (
    // Fundo azul usando a imagem 'fundo.png' e centralizando o conteúdo
    <div
      className="min-h-screen bg-cover bg-center text-white flex flex-col justify-center items-center"
      style={{ backgroundImage: "url('/assets/fundo.png')" }} // Usando a imagem de fundo
    >
      {/* Logotipo COGEL no canto superior esquerdo com o texto "COGEL" */}
      <div className="absolute top-4 left-4">
        {/* Usando o logo.png que tem o escudo e o texto "COGEL" */}
        {/* Certifique-se de que logo.png está em /public/ */}
        <img
          src="/assets/logocogel.jpg" // Caminho relativo à pasta 'public'
          alt="COGEL Logo"
          className="w-38 h-auto" // Ajuste o tamanho conforme necessário
        />
        {/* O texto "Companhia de Governança Eletrônica do Salvador" não estava no código anterior, mas se for para adicionar: */}
        {/* <p className="text-xs font-semibold text-white mt-1">Companhia de Governança Eletrônica do Salvador</p> */}
      </div>

      {/* Conteúdo Central: Botões de Navegação */}
      {/* h-[calc(100vh-64px)] era usado antes com um header. Aqui, centralizamos em relação à tela cheia. */}
      {/* space-x-12 é para o espaçamento entre os botões */}
      <div className="flex justify-center items-center h-full"> {/* Mantém o flex e centralização */}
        <div className="flex space-x-12"> {/* Usando space-x-12 para espaçamento horizontal */}
          {/* Botão Relatórios */}
          <div
            className="bg-white rounded-lg p-6 text-center text-black shadow-lg hover:scale-105 transition-transform
                       w-40 h-40 cursor-pointer flex flex-col items-center justify-center"
            onClick={() => navigate('/relatorios')}
          >
            {/* Ícone de Relatórios - certifique-se de que está em /public/assets/ */}
            <img
              src="/assets/icone-relatorios.png"
              alt="Relatórios"
              className="w-16 h-16 mx-auto mb-2"
            />
            <p className="text-lg font-medium">Relatórios</p>
          </div>

          {/* Botão Scans */}
          <div
            className="bg-white rounded-lg p-6 text-center text-black shadow-lg hover:scale-105 transition-transform
                       w-40 h-40 cursor-pointer flex flex-col items-center justify-center"
            onClick={() => navigate('/scans')}
          >
            {/* Ícone de Scans - certifique-se de que está em /public/assets/ */}
            <img
              src="/assets/icone-scan.png"
              alt="Scans"
              className="w-18 h-16 mx-auto mb-2"
            />
            <p className="text-lg font-medium">Scans</p>
          </div>

          {/* Botão Gerenciar Vulnerabilidades */}
          <div
            className="bg-white rounded-lg p-6 text-center text-black shadow-lg hover:scale-105 transition-transform
                       w-40 h-40 cursor-pointer flex flex-col items-center justify-center"
            onClick={() => navigate('/gerenciar-vulnerabilidades')}
          >
            {/* Ícone de Gerenciar Vulnerabilidades - certifique-se de que está em /public/assets/ */}
            <img
              src="/assets/icone-gerenciar-vulnerabilidades.png"
              alt="Gerenciar Vulnerabilidades"
              className="w-16 h-16 mx-auto mb-2"
            />
            <p className="text-lg font-medium">Gerenciar Vulnerabilidades</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Home;