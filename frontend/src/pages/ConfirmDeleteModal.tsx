import React from 'react';

interface ConfirmDeleteModalProps {
  isOpen: boolean; // Se o modal está aberto
  onClose: () => void; // Função para fechar o modal
  onConfirm: () => void; // Função a ser chamada quando o usuário confirma
  message: string; // Mensagem de confirmação (ex: "Tem certeza que deseja apagar o relatório X?")
}

const ConfirmDeleteModal: React.FC<ConfirmDeleteModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  message,
}) => {
  if (!isOpen) return null; // Não renderiza nada se o modal não estiver aberto

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white p-6 rounded-lg shadow-xl max-w-sm w-full m-4">
        <h2 className="text-xl font-bold text-gray-800 mb-4">Confirmar Exclusão</h2>
        <p className="text-gray-700 mb-6">{message}</p>
        <div className="flex justify-end space-x-3">
          <button
            onClick={onClose}
            className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-2 px-4 rounded transition duration-300"
          >
            Cancelar
          </button>
          <button
            onClick={onConfirm}
            className="bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded transition duration-300"
          >
            Confirmar
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConfirmDeleteModal;