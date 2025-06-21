import { useNavigate } from 'react-router-dom';

function Home() {
  const navigate = useNavigate();

  return (

    <div className="relative flex-grow flex flex-col justify-center items-center text-white">
      {/* Logotipo COGEL (opcional, pode ser mantido se o design exigir) */}
      <div className="absolute top-1/2 left-12 -translate-y-1/2">
        <img
          src="/assets/logocogel.jpg"
          alt="COGEL Logo"
          className="w-38 h-auto"
        />
      </div>

      {/* Conteúdo Central: Botões de Navegação */}
      <div className="flex space-x-12">
        {/* Botão Relatórios */}
        <div
          className="bg-white rounded-lg p-6 text-center text-black shadow-lg hover:scale-105 transition-transform
                     w-40 h-40 cursor-pointer flex flex-col items-center justify-center"
          onClick={() => navigate('/relatorios')}
        >
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
          <img
            src="/assets/icone-gerenciar-vulnerabilidades.png"
            alt="Gerenciar Vulnerabilidades"
            className="w-16 h-16 mx-auto mb-2"
          />
          <p className="text-lg font-medium">Gerenciar Vulnerabilidades</p>
        </div>
      </div>
    </div>
  );
}

export default Home;