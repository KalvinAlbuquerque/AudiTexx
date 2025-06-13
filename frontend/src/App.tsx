import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import './App.css';
import './index.css';

// Importa os componentes de layout
import Header from './components/Header'; // Importa o componente Header
import Footer from './components/Footer'; // Importa o componente Footer (se você tiver um)

// Importa os componentes de página
import Home from './pages/Home';
import CriarLista from './pages/CriarLista';
import ListaDeScans from './pages/ListaDeScans';
import EditarLista from './pages/EditarLista';
import GerarRelatorio from './pages/GerarRelatorio';
import GerarRelatorioFinal from './pages/GerarRelatorioFinal';
import Relatorios from './pages/Relatorios';
import RelatoriosGerados from './pages/RelatoriosGerados';
import Scans from './pages/Scans';
import PesquisarScanWAS from './pages/PesquisarScanWAS';
import PesquisarScanVM from './pages/PesquisarScanVM';
import GerenciarVulnerabilidades from './pages/GerenciarVulnerabilidades';
import ManageTenableApiKeys from './pages/ManageTenableApiKeys'; 

function App() {
    return (
        <Router>
            {/* O Header será exibido em todas as páginas */}
            <Header /> 
            <main className="flex-grow"> {/* Adicionado flex-grow para que o conteúdo preencha o espaço */}
                <Routes>
                    <Route path="/" element={<Home />} />
                    <Route path="/criar-lista" element={<CriarLista />} />
                    <Route path="/lista-de-scans" element={<ListaDeScans />} />
                    <Route path="/editar-lista/:idLista" element={<EditarLista />} />
                    <Route path="/gerar-relatorio/:idLista" element={<GerarRelatorio />} />
                    <Route path="/gerar-relatorio-final/:relatorioId" element={<GerarRelatorioFinal />} />
                    <Route path="/relatorios" element={<Relatorios />} />
                    <Route path="/relatorios-gerados" element={<RelatoriosGerados />} />
                    <Route path="/scans" element={<Scans />} />
                    <Route path="/pesquisar-scan-was" element={<PesquisarScanWAS />} />
                    <Route path="/pesquisar-scan-vm" element={<PesquisarScanVM />} />
                    <Route path="/gerenciar-vulnerabilidades" element={<GerenciarVulnerabilidades />} />
                    <Route path="/manage-tenable-api-keys" element={<ManageTenableApiKeys />} />
                </Routes>
            </main>
            {/* O Footer também será exibido em todas as páginas */}
            <Footer />
        </Router>
    );
}

export default App;
