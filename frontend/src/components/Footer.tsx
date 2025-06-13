function Footer() {
  const currentYear = new Date().getFullYear(); // Obtém o ano atual dinamicamente

  return (
    <footer className="bg-gray-800 text-white p-4 text-center shadow-inner mt-auto">
      <div className="container mx-auto">
        <p>&copy; {currentYear} Auditex. Todos os direitos reservados.</p>
        {/* Você pode adicionar mais conteúdo aqui, como links para redes sociais, política de privacidade, etc. */}
      </div>
    </footer>
  );
}

export default Footer;