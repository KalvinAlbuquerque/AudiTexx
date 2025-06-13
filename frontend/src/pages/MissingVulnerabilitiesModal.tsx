import React from 'react';
import { toast } from 'react-toastify'; // Importar toast

interface MissingVulnerabilitiesModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  vulnerabilities: string[]; // Lista de nomes de vulnerabilidades
}

const MissingVulnerabilitiesModal: React.FC<MissingVulnerabilitiesModalProps> = ({
  isOpen,
  onClose,
  title,
  vulnerabilities,
}) => {
  if (!isOpen) return null;

  const handleCopy = () => {
    if (vulnerabilities.length > 0) {
      const textToCopy = vulnerabilities.join('\n');
      navigator.clipboard.writeText(textToCopy)
        .then(() => {
          toast.success('Vulnerabilidades copiadas para a área de transferência!'); // Alterado de alert para toast
        })
        .catch(err => {
          console.error('Erro ao copiar vulnerabilidades:', err);
          toast.error('Falha ao copiar vulnerabilidades.'); // Alterado de alert para toast
        });
    }
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white p-6 rounded-lg shadow-xl max-w-lg w-full m-4">
        <h2 className="text-xl font-bold text-gray-800 mb-4">{title}</h2>
        {vulnerabilities.length > 0 ? (
          <ul className="list-disc list-inside h-64 overflow-y-auto mb-4 p-2 border rounded bg-gray-50">
            {vulnerabilities.map((vuln, index) => (
              <li key={index} className="text-gray-700">{vuln}</li>
            ))}
          </ul>
        ) : (
          <p className="text-gray-600 mb-4">Nenhuma vulnerabilidade ausente.</p>
        )}
        <div className="flex justify-end space-x-3">
          {vulnerabilities.length > 0 && (
            <button
              onClick={handleCopy}
              className="bg-[#007BB4] hover:bg-[#009BE2] text-white font-bold py-2 px-4 rounded transition duration-300"
            >
              Copiar Todas
            </button>
          )}
          <button
            onClick={onClose}
            className="bg-[#007BB4] hover:bg-[#009BE2] text-white font-bold py-2 px-4 rounded transition duration-300"
          >
            Fechar
          </button>
        </div>
      </div>
    </div>
  );
};

export default MissingVulnerabilitiesModal;