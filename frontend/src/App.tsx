import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import './App.css';
import './index.css';

// Importa os componentes de página, incluindo a nova Home
import Home from './pages/Home'; // AGORA IMPORTAMOS A HOME
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

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<Home />} /> {/* CORREÇÃO: A rota raiz agora aponta para Home */}
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
            </Routes>
        </Router>
    );
}

export default App;