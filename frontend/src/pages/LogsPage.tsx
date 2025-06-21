// frontend/src/pages/LogsPage.tsx

import React, { useState, useEffect, useContext } from 'react';
import { getLogs, getAllUsers } from '../api/backendApi';
import { AuthContext } from '../context/AuthContext';

// Tipagem para um registro de log
interface LogEntry {
  _id: string;
  username: string;
  action: string;
  timestamp: string;
  details: Record<string, any>;
}

const LogsPage: React.FC = () => {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [users, setUsers] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Estado para filtros
  const [filters, setFilters] = useState({
    username: '',
    action: '',
    date: '',
  });

  // Estado para paginação
  const [pagination, setPagination] = useState({
    currentPage: 1,
    totalPages: 1,
  });

  const auth = useContext(AuthContext);

  if (!auth) {
    return (
        <div className="container mx-auto p-4">
          <p>Carregando informações de autenticação...</p>
        </div>
    );
  }
  
  const { token } = auth; // Agora é seguro desestruturar o token

  const fetchLogsData = () => {
    if (!token) return;
    setLoading(true);
    
    const params = {
      page: pagination.currentPage,
      limit: 20,
      username: filters.username || undefined,
      action: filters.action || undefined,
      date: filters.date || undefined,
    };

    getLogs(token, params)
      .then(data => {
        setLogs(data.logs);
        setPagination(prev => ({ ...prev, totalPages: data.total_pages }));
        setError('');
      })
      .catch(err => {
        console.error('Erro ao buscar logs:', err);
        setError('Falha ao carregar os logs. Tente novamente.');
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    // Busca a lista de usuários para o dropdown de filtro
    if (!token) return;
    getAllUsers(token)
      .then(setUsers)
      .catch(err => console.error("Falha ao buscar usuários:", err));
  }, [token]);

  // Removido 'filters' do array de dependência para evitar múltiplas chamadas
  // A chamada agora é feita pelo botão ou mudança de página.
  // Para carregar na primeira vez, podemos chamar diretamente.
  useEffect(() => {
    fetchLogsData();
  }, [token, pagination.currentPage]); 

  const handleApplyFilters = () => {
    setPagination(prev => ({ ...prev, currentPage: 1 }));
    // A busca será acionada pelo useEffect acima quando a página ou filtros mudarem
    // Forçamos uma nova busca se os filtros foram aplicados na mesma página
    fetchLogsData();
  };

  const handleFilterChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFilters(prev => ({ ...prev, [name]: value }));
  };
  
  const handleClearFilters = () => {
    const newFilters = { username: '', action: '', date: '' };
    if (filters.username !== '' || filters.action !== '' || filters.date !== '') {
      setFilters(newFilters);
      setPagination(prev => ({ ...prev, currentPage: 1 }));
      // Força a atualização após limpar
      if (pagination.currentPage === 1) {
        if (!token) return;
        getLogs(token, { page: 1, limit: 20 }).then(data => {
          setLogs(data.logs);
          setPagination(prev => ({ ...prev, totalPages: data.total_pages }));
        });
      }
    }
  };

  const handlePageChange = (newPage: number) => {
    setPagination(prev => ({ ...prev, currentPage: newPage }));
  };

  const logActions = ['generate_report', 'download_report', 'create_user'];

  return (
      <div className="container mx-auto p-4">
        <h1 className="text-2xl font-bold mb-4">Registros de Atividade (Logs)</h1>
        
        <div className="bg-gray-100 p-4 rounded-lg mb-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          <select name="username" value={filters.username} onChange={handleFilterChange} className="p-2 border rounded">
            <option value="">Todos os Usuários</option>
            {users.map(user => <option key={user} value={user}>{user}</option>)}
          </select>
          <select name="action" value={filters.action} onChange={handleFilterChange} className="p-2 border rounded">
            <option value="">Todas as Ações</option>
            {logActions.map(action => <option key={action} value={action}>{action}</option>)}
          </select>
          <input type="date" name="date" value={filters.date} onChange={handleFilterChange} className="p-2 border rounded" />
          <button onClick={handleApplyFilters} className="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded">
            Aplicar Filtros
          </button>
          <button onClick={handleClearFilters} className="bg-gray-500 hover:bg-gray-600 text-white font-bold py-2 px-4 rounded">
            Limpar Filtros
          </button>
        </div>

        {loading && <p>Carregando...</p>}
        {error && <p className="text-red-500">{error}</p>}

        {!loading && !error && (
          <>
            <div className="overflow-x-auto">
              <table className="min-w-full bg-white border">
                <thead className="bg-gray-800 text-white">
                  <tr>
                    <th className="py-2 px-4 text-left">Data/Hora</th>
                    <th className="py-2 px-4 text-left">Usuário</th>
                    <th className="py-2 px-4 text-left">Ação</th>
                    <th className="py-2 px-4 text-left">Detalhes</th>
                  </tr>
                </thead>
                <tbody>
                  {logs.length > 0 ? logs.map(log => (
                    <tr key={log._id} className="border-b hover:bg-gray-100">
                      <td className="py-2 px-4">{new Date(log.timestamp).toLocaleString('pt-BR')}</td>
                      <td className="py-2 px-4">{log.username}</td>
                      <td className="py-2 px-4">{log.action}</td>
                      <td className="py-2 px-4">
                        <pre className="bg-gray-200 p-2 rounded text-xs whitespace-pre-wrap break-all">{JSON.stringify(log.details, null, 2)}</pre>
                      </td>
                    </tr>
                  )) : (
                    <tr>
                      <td colSpan={4} className="text-center py-4">Nenhum registro encontrado.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            <div className="flex justify-between items-center mt-4">
              <button 
                onClick={() => handlePageChange(pagination.currentPage - 1)} 
                disabled={pagination.currentPage === 1 || loading}
                className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded disabled:bg-gray-400"
              >
                Anterior
              </button>
              <span>Página {pagination.currentPage} de {pagination.totalPages}</span>
              <button 
                onClick={() => handlePageChange(pagination.currentPage + 1)} 
                disabled={pagination.currentPage >= pagination.totalPages || loading}
                className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded disabled:bg-gray-400"
              >
                Próxima
              </button>
            </div>
          </>
        )}
      </div>
  );
};

export default LogsPage;