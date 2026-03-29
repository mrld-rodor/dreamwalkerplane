/**
 * translations.js - DreamWalker Plane
 * Sistema de tradução em JavaScript
 * Idiomas: Português (pt), English (en), Español (es)
 */

const TRANSLATIONS = {
    // Português (padrão)
    pt: {
        // Navegação
        'nav_inicio': 'Início',
        'nav_contos': 'Contos',
        'nav_mural': 'Mural',
        'nav_doacoes': 'Doações',
        'nav_contato': 'Contato',
        'nav_sonhar': 'O Sonhar',
        'nav_admin': 'Admin',
        
        // Página Inicial
        'welcome': 'Bem-vindo ao DreamWalker Plane',
        'intro_text': 'Um portal onde os limites entre a realidade e o imaginário se desvanecem. Aqui, cada conto é uma chave para mundos desconhecidos, guiando você por trilhas oníricas e experiências além do consciente.',
        'ready_question': 'Está preparado para andar entre os sonhos?',
        'btn_contos': 'Contos',
        'btn_mural': 'Mural de Relatos',
        'btn_contato': 'Contato',
        'btn_sonhar': 'O Sonhar',
        
        // Contos
        'fragmentos': 'Fragmentos Oníricos',
        'download_gratis': 'Download Grátis',
        'comprar_hotmart': 'Comprar na Hotmart',
        'conto_intro': 'Imagine uma linha do tempo como uma cachoeira que flui através dos sonhos. Cada conto é um fragmento de sonho que emerge dessa corrente, revelando-se para aqueles prontos a desvendar seus segredos.',
        'conto_002_titulo': 'O Carnaval',
        'conto_002_desc': 'O conto que nasceu de uma série de intensos sonhos lúcidos, onde o subconsciente nos conduz por caminhos enigmáticos.',
        'conto_001_titulo': 'O Trem',
        'conto_001_desc': 'Um conto surreal e enigmático, no qual um grupo de jovens presencia um trem misterioso com inscrições desconhecidas.',
        'conto_000_titulo': 'O Grande Livro',
        'conto_000_desc': 'Um conto com atmosfera de mistério, suspense e toque filosófico, onde o protagonista é levado a um campo de batalha.',
        
        // Mural
        'mural_titulo': 'Mural dos Sonhadores',
        'mural_subtitulo': 'Relatos enviados por viajantes oníricos como você. Cada história é um fragmento de um sonho, uma janela para mundos desconhecidos.',
        'btn_compartilhar': 'Compartilhar meu relato',
        'nenhum_relato': 'Nenhum relato ainda',
        'seja_primeiro': 'Seja o primeiro a compartilhar sua experiência onírica!',
        'relato_compartilhado': 'Relato compartilhado',
        'por': 'por',
        'enviado_em': 'Enviado em',
        
        // Formulário de Relato
        'enviar_relato_titulo': 'Compartilhe seu Relato',
        'enviar_relato_sub': 'Suas experiências oníricas podem inspirar outros sonhadores.',
        'moderacao_aviso': 'Relatos passam por moderação antes de aparecerem no mural',
        'label_autor': 'Seu nome',
        'label_titulo': 'Título do relato',
        'label_conteudo': 'Seu relato',
        'placeholder_autor': 'Como você gostaria de ser chamado?',
        'placeholder_titulo': 'Dê um título para sua experiência...',
        'placeholder_conteudo': 'Compartilhe sua experiência onírica...\n\nO que você viu? O que sentiu? Que mundos visitou?',
        'btn_enviar': 'Enviar Relato',
        'btn_voltar': 'Voltar ao Mural',
        'dica_relato': 'Relatos autênticos e bem escritos têm mais chances de serem aprovados',
        
        // Doações
        'doacoes_titulo': 'Apoie o Sonho',
        'doacoes_sub': 'Cada contribuição é um eco de apoio, uma faísca que ilumina os recantos mais sombrios da criação.',
        'contribuicao_voluntaria': 'Contribuição Voluntária',
        'contribuicao_texto': 'Os contos são gratuitos, mas se você deseja apoiar o projeto, qualquer contribuição é bem-vinda.',
        'doar_paypal': 'Doar via PayPal',
        'adquira_contos': 'Adquira os Contos',
        'adquira_texto': 'Leia gratuitamente no site ou adquira sua cópia digital na Hotmart.',
        'pagamento_seguro': 'Pagamento Seguro',
        'formato_pdf': 'Formato PDF',
        'acesso_imediato': 'Acesso Imediato',
        'preco': 'R$ 9,90',
        
        // Contato
        'contato_titulo': 'Mapa Onírico',
        'contato_sub': 'O Mapa Onírico é a bússola que guia sua jornada até os mistérios do DreamWalker.',
        'conecte_se': 'Conecte-se',
        'quem_somos': 'DreamWalker Plane',
        'quem_somos_texto': 'Um projeto experimental que mergulha nas fronteiras entre os sonhos humanos e as capacidades da inteligência artificial.',
        'envie_mensagem': 'Envie uma Mensagem',
        'envie_mensagem_texto': 'Enviar uma mensagem ao DreamWalker é lançar suas palavras no desconhecido.',
        'label_nome': 'Seu nome',
        'label_email': 'Seu email',
        'label_mensagem': 'Sua mensagem',
        'placeholder_nome': 'Como você se chama?',
        'placeholder_email': 'seu@email.com',
        'placeholder_mensagem': 'Escreva sua mensagem aqui...',
        'btn_enviar_mensagem': 'Enviar Mensagem',
        'btn_apoiar': 'Apoiar o Projeto',
        
        // O Sonhar
        'sonhar_texto': 'A construção deste portal está longe de ser simples. Algo no ar, invisível aos olhos, desafia nossa jornada. A página está em manutenção, mas algo mais profundo e misterioso está em jogo. O portal logo se abrirá, mas até lá, o mistério permanece.',
        
        // Status
        'status_titulo': 'Status do Portal',
        'visitantes': 'Visitantes',
        'downloads': 'Downloads',
        'historico_visitas': 'Histórico de Visitas',
        'data': 'Data',
        'localizacao': 'Localização',
        'ip': 'IP',
        'os': 'Sistema Operacional',
        'nenhuma_visita': 'Nenhuma visita registrada ainda.',
        
        // Footer
        'todos_direitos': 'Todos os direitos reservados',
        'politica_privacidade': 'Política de Privacidade',
        'termos_uso': 'Termos de Uso',
        
        // Admin
        'admin_login_titulo': 'Área Administrativa',
        'admin_login_sub': 'Acesso restrito - CRUD de Relatos',
        'usuario': 'Usuário',
        'senha': 'Senha',
        'btn_acessar': 'Acessar',
        'acesso_restrito': 'Esta área é restrita aos administradores do site',
        'dashboard': 'Dashboard',
        'gerenciar_relatos': 'Gerenciar Relatos',
        'sair': 'Sair',
        'total_relatos': 'Total Relatos',
        'pendentes': 'Pendentes',
        'aprovados': 'Aprovados',
        'rejeitados': 'Rejeitados',
        'ultimos_relatos': 'Últimos Relatos',
        'status_pendente': 'Pendente',
        'status_aprovado': 'Aprovado',
        'status_rejeitado': 'Rejeitado',
        'btn_aprovar': 'Aprovar',
        'btn_rejeitar': 'Rejeitar',
        'btn_editar': 'Editar',
        'btn_excluir': 'Excluir',
        'btn_voltar': 'Voltar',
        'btn_salvar': 'Salvar',
        'btn_cancelar': 'Cancelar',
        'conteudo': 'Conteúdo',
        'confirmar_exclusao': 'Tem certeza que deseja excluir este relato permanentemente?',
        
        // Mensagens de feedback
        'feedback_relato_enviado': 'Seu relato foi enviado com sucesso! Aguarde a aprovação.',
        'feedback_mensagem_enviada': 'Mensagem enviada com sucesso! Entrarei em contato em breve.',
        'feedback_login_sucesso': 'Login realizado com sucesso!',
        'feedback_login_erro': 'Usuário ou senha inválidos!',
    },
    
    // English
    en: {
        'nav_inicio': 'Home',
        'nav_contos': 'Stories',
        'nav_mural': 'Wall',
        'nav_doacoes': 'Donate',
        'nav_contato': 'Contact',
        'nav_sonhar': 'The Dream',
        'nav_admin': 'Admin',
        
        'welcome': 'Welcome to DreamWalker Plane',
        'intro_text': 'A portal where the boundaries between reality and imagination fade away. Here, each story is a key to unknown worlds, guiding you through dreamlike paths and experiences beyond consciousness.',
        'ready_question': 'Are you ready to walk among dreams?',
        'btn_contos': 'Stories',
        'btn_mural': 'Story Wall',
        'btn_contato': 'Contact',
        'btn_sonhar': 'The Dream',
        
        'fragmentos': 'Dream Fragments',
        'download_gratis': 'Free Download',
        'comprar_hotmart': 'Buy on Hotmart',
        'conto_intro': 'Imagine a timeline like a waterfall flowing through dreams. Each story is a dream fragment emerging from this current.',
        'conto_002_titulo': 'The Carnival',
        'conto_002_desc': 'The story born from a series of intense lucid dreams, where the subconscious leads us through enigmatic paths.',
        'conto_001_titulo': 'The Train',
        'conto_001_desc': 'A surreal and enigmatic tale in which a group of young people witness a mysterious train with unknown inscriptions.',
        'conto_000_titulo': 'The Great Book',
        'conto_000_desc': 'A story with an atmosphere of mystery, suspense and philosophical touch.',
        
        'mural_titulo': 'Dreamers Wall',
        'mural_subtitulo': 'Reports sent by dream travelers like you. Each story is a fragment of a dream.',
        'btn_compartilhar': 'Share my story',
        'nenhum_relato': 'No stories yet',
        'seja_primeiro': 'Be the first to share your dream experience!',
        'relato_compartilhado': 'Story shared',
        'por': 'by',
        'enviado_em': 'Sent on',
        
        'enviar_relato_titulo': 'Share Your Story',
        'enviar_relato_sub': 'Your dream experiences can inspire other dreamers.',
        'moderacao_aviso': 'Stories go through moderation before appearing on the wall',
        'label_autor': 'Your name',
        'label_titulo': 'Story title',
        'label_conteudo': 'Your story',
        'placeholder_autor': 'What would you like to be called?',
        'placeholder_titulo': 'Give a title to your experience...',
        'placeholder_conteudo': 'Share your dream experience...\n\nWhat did you see? What did you feel?',
        'btn_enviar': 'Send Story',
        'btn_voltar': 'Back to Wall',
        'dica_relato': 'Authentic and well-written stories are more likely to be approved',
        
        'doacoes_titulo': 'Support the Dream',
        'doacoes_sub': 'Each contribution is an echo of support, a spark that illuminates the darkest corners of creation.',
        'contribuicao_voluntaria': 'Voluntary Contribution',
        'contribuicao_texto': 'The stories are free, but if you want to support the project, any contribution is welcome.',
        'doar_paypal': 'Donate via PayPal',
        'adquira_contos': 'Get the Stories',
        'adquira_texto': 'Read for free on the site or get your digital copy on Hotmart.',
        'pagamento_seguro': 'Secure Payment',
        'formato_pdf': 'PDF Format',
        'acesso_imediato': 'Instant Access',
        'preco': '$9.90 USD',
        
        'contato_titulo': 'Dream Map',
        'contato_sub': 'The Dream Map is the compass that guides your journey to the mysteries of DreamWalker.',
        'conecte_se': 'Connect',
        'quem_somos': 'DreamWalker Plane',
        'quem_somos_texto': 'An experimental project that delves into the boundaries between human dreams and artificial intelligence.',
        'envie_mensagem': 'Send a Message',
        'envie_mensagem_texto': 'Sending a message to DreamWalker is launching your words into the unknown.',
        'label_nome': 'Your name',
        'label_email': 'Your email',
        'label_mensagem': 'Your message',
        'placeholder_nome': 'What is your name?',
        'placeholder_email': 'your@email.com',
        'placeholder_mensagem': 'Write your message here...',
        'btn_enviar_mensagem': 'Send Message',
        'btn_apoiar': 'Support the Project',
        
        'sonhar_texto': 'The construction of this portal is far from simple. Something in the air challenges our journey. The page is under maintenance, but something deeper and more mysterious is at play.',
        
        'status_titulo': 'Portal Status',
        'visitantes': 'Visitors',
        'downloads': 'Downloads',
        'historico_visitas': 'Visit History',
        'data': 'Date',
        'localizacao': 'Location',
        'ip': 'IP',
        'os': 'OS',
        'nenhuma_visita': 'No visits recorded yet.',
        
        'todos_direitos': 'All rights reserved',
        'politica_privacidade': 'Privacy Policy',
        'termos_uso': 'Terms of Use',
        
        'admin_login_titulo': 'Admin Area',
        'admin_login_sub': 'Restricted access - Stories CRUD',
        'usuario': 'Username',
        'senha': 'Password',
        'btn_acessar': 'Access',
        'acesso_restrito': 'This area is restricted to site administrators',
        'dashboard': 'Dashboard',
        'gerenciar_relatos': 'Manage Stories',
        'sair': 'Logout',
        'total_relatos': 'Total Stories',
        'pendentes': 'Pending',
        'aprovados': 'Approved',
        'rejeitados': 'Rejected',
        'ultimos_relatos': 'Latest Stories',
        'status_pendente': 'Pending',
        'status_aprovado': 'Approved',
        'status_rejeitado': 'Rejected',
        'btn_aprovar': 'Approve',
        'btn_rejeitar': 'Reject',
        'btn_editar': 'Edit',
        'btn_excluir': 'Delete',
        'btn_voltar': 'Back',
        'btn_salvar': 'Save',
        'btn_cancelar': 'Cancel',
        'conteudo': 'Content',
        'confirmar_exclusao': 'Are you sure you want to permanently delete this story?',
        
        'feedback_relato_enviado': 'Your story has been sent successfully! Wait for approval.',
        'feedback_mensagem_enviada': 'Message sent successfully! I will contact you soon.',
        'feedback_login_sucesso': 'Login successful!',
        'feedback_login_erro': 'Invalid username or password!',
    },
    
    // Español
    es: {
        'nav_inicio': 'Inicio',
        'nav_contos': 'Cuentos',
        'nav_mural': 'Mural',
        'nav_doacoes': 'Donaciones',
        'nav_contato': 'Contacto',
        'nav_sonhar': 'El Soñar',
        'nav_admin': 'Admin',
        
        'welcome': 'Bienvenido a DreamWalker Plane',
        'intro_text': 'Un portal donde los límites entre la realidad y la imaginación se desvanecen. Cada cuento es una llave a mundos desconocidos.',
        'ready_question': '¿Estás preparado para caminar entre sueños?',
        'btn_contos': 'Cuentos',
        'btn_mural': 'Mural de Relatos',
        'btn_contato': 'Contacto',
        'btn_sonhar': 'El Soñar',
        
        'fragmentos': 'Fragmentos Oníricos',
        'download_gratis': 'Descarga Gratis',
        'comprar_hotmart': 'Comprar en Hotmart',
        'conto_intro': 'Imagina una línea de tiempo como una cascada que fluye a través de los sueños. Cada cuento es un fragmento de sueño.',
        'conto_002_titulo': 'El Carnaval',
        'conto_002_desc': 'El cuento que nació de una serie de intensos sueños lúcidos, donde el subconsciente nos guía por caminos enigmáticos.',
        'conto_001_titulo': 'El Tren',
        'conto_001_desc': 'Un relato surrealista y enigmático, donde un grupo de jóvenes presencia un tren misterioso.',
        'conto_000_titulo': 'El Gran Libro',
        'conto_000_desc': 'Un cuento con atmósfera de misterio, suspenso y toque filosófico.',
        
        'mural_titulo': 'Mural de Soñadores',
        'mural_subtitulo': 'Relatos enviados por viajeros oníricos como tú. Cada historia es un fragmento de un sueño.',
        'btn_compartilhar': 'Compartir mi relato',
        'nenhum_relato': 'No hay relatos aún',
        'seja_primeiro': '¡Sé el primero en compartir tu experiencia onírica!',
        'relato_compartilhado': 'Relato compartido',
        'por': 'por',
        'enviado_em': 'Enviado el',
        
        'enviar_relato_titulo': 'Comparte tu Relato',
        'enviar_relato_sub': 'Tus experiencias oníricas pueden inspirar a otros soñadores.',
        'moderacao_aviso': 'Los relatos pasan por moderación antes de aparecer en el mural',
        'label_autor': 'Tu nombre',
        'label_titulo': 'Título del relato',
        'label_conteudo': 'Tu relato',
        'placeholder_autor': '¿Cómo te gustaría que te llamen?',
        'placeholder_titulo': 'Da un título a tu experiencia...',
        'placeholder_conteudo': 'Comparte tu experiencia onírica...\n\n¿Qué viste? ¿Qué sentiste?',
        'btn_enviar': 'Enviar Relato',
        'btn_voltar': 'Volver al Mural',
        'dica_relato': 'Los relatos auténticos y bien escritos tienen más probabilidades de ser aprobados',
        
        'doacoes_titulo': 'Apoya el Sueño',
        'doacoes_sub': 'Cada contribución es un eco de apoyo, una chispa que ilumina los rincones más oscuros de la creación.',
        'contribuicao_voluntaria': 'Contribución Voluntaria',
        'contribuicao_texto': 'Los cuentos son gratuitos, pero si deseas apoyar el proyecto, cualquier contribución es bienvenida.',
        'doar_paypal': 'Donar vía PayPal',
        'adquira_contos': 'Adquiere los Cuentos',
        'adquira_texto': 'Lee gratis en el sitio o adquiere tu copia digital en Hotmart.',
        'pagamento_seguro': 'Pago Seguro',
        'formato_pdf': 'Formato PDF',
        'acesso_imediato': 'Acceso Inmediato',
        'preco': '$9.90 USD',
        
        'contato_titulo': 'Mapa Onírico',
        'contato_sub': 'El Mapa Onírico es la brújula que guía tu viaje a los misterios de DreamWalker.',
        'conecte_se': 'Conéctate',
        'quem_somos': 'DreamWalker Plane',
        'quem_somos_texto': 'Un proyecto experimental que se sumerge en las fronteras entre los sueños humanos y la inteligencia artificial.',
        'envie_mensagem': 'Envía un Mensaje',
        'envie_mensagem_texto': 'Enviar un mensaje a DreamWalker es lanzar tus palabras a lo desconocido.',
        'label_nome': 'Tu nombre',
        'label_email': 'Tu email',
        'label_mensagem': 'Tu mensaje',
        'placeholder_nome': '¿Cómo te llamas?',
        'placeholder_email': 'tu@email.com',
        'placeholder_mensagem': 'Escribe tu mensaje aquí...',
        'btn_enviar_mensagem': 'Enviar Mensaje',
        'btn_apoiar': 'Apoyar el Proyecto',
        
        'sonhar_texto': 'La construcción de este portal está lejos de ser simple. Algo en el aire desafía nuestro viaje. La página está en mantenimiento, pero algo más profundo y misterioso está en juego.',
        
        'status_titulo': 'Estado del Portal',
        'visitantes': 'Visitantes',
        'downloads': 'Descargas',
        'historico_visitas': 'Historial de Visitas',
        'data': 'Fecha',
        'localizacao': 'Ubicación',
        'ip': 'IP',
        'os': 'SO',
        'nenhuma_visita': 'Aún no se han registrado visitas.',
        
        'todos_direitos': 'Todos los derechos reservados',
        'politica_privacidade': 'Política de Privacidad',
        'termos_uso': 'Términos de Uso',
        
        'admin_login_titulo': 'Área Administrativa',
        'admin_login_sub': 'Acceso restringido - CRUD de Relatos',
        'usuario': 'Usuario',
        'senha': 'Contraseña',
        'btn_acessar': 'Acceder',
        'acesso_restrito': 'Esta área es restringida para administradores',
        'dashboard': 'Panel',
        'gerenciar_relatos': 'Gestionar Relatos',
        'sair': 'Salir',
        'total_relatos': 'Total Relatos',
        'pendentes': 'Pendientes',
        'aprovados': 'Aprobados',
        'rejeitados': 'Rechazados',
        'ultimos_relatos': 'Últimos Relatos',
        'status_pendente': 'Pendiente',
        'status_aprovado': 'Aprobado',
        'status_rejeitado': 'Rechazado',
        'btn_aprovar': 'Aprobar',
        'btn_rejeitar': 'Rechazar',
        'btn_editar': 'Editar',
        'btn_excluir': 'Eliminar',
        'btn_voltar': 'Volver',
        'btn_salvar': 'Guardar',
        'btn_cancelar': 'Cancelar',
        'conteudo': 'Contenido',
        'confirmar_exclusao': '¿Estás seguro de que deseas eliminar este relato permanentemente?',
        
        'feedback_relato_enviado': '¡Tu relato ha sido enviado con éxito! Espera la aprobación.',
        'feedback_mensagem_enviada': '¡Mensaje enviado con éxito! Me pondré en contacto pronto.',
        'feedback_login_sucesso': '¡Inicio de sesión exitoso!',
        'feedback_login_erro': '¡Usuario o contraseña inválidos!',
    }
};

// Idioma atual (padrão pt)
let currentLang = 'pt';

// Função para obter tradução
function t(key) {
    return TRANSLATIONS[currentLang][key] || TRANSLATIONS['pt'][key] || key;
}

// Função para traduzir a página inteira
function translatePage() {
    // Traduz elementos com data-lang
    document.querySelectorAll('[data-lang]').forEach(el => {
        const key = el.getAttribute('data-lang');
        if (TRANSLATIONS[currentLang][key]) {
            if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
                el.placeholder = t(key);
            } else {
                el.textContent = t(key);
            }
        }
    });
    
    // Traduz placeholders
    document.querySelectorAll('[data-lang-placeholder]').forEach(el => {
        const key = el.getAttribute('data-lang-placeholder');
        if (TRANSLATIONS[currentLang][key]) {
            el.placeholder = t(key);
        }
    });
}

// Função para mudar o idioma
function setLanguage(lang) {
    if (TRANSLATIONS[lang]) {
        currentLang = lang;
        localStorage.setItem('dreamwalker_lang', lang);
        translatePage();
        updateLangButton(lang);
    }
}

// Atualiza o botão de idioma
function updateLangButton(lang) {
    const btn = document.getElementById('langBtnText');
    if (btn) {
        const flags = { pt: '🇧🇷 PT', en: '🇺🇸 EN', es: '🇪🇸 ES' };
        btn.textContent = flags[lang] || '🇧🇷 PT';
    }
}

// Carrega o idioma salvo
function loadSavedLanguage() {
    const saved = localStorage.getItem('dreamwalker_lang');
    if (saved && TRANSLATIONS[saved]) {
        currentLang = saved;
    } else {
        currentLang = 'pt';
    }
    translatePage();
    updateLangButton(currentLang);
}

// Inicializa quando a página carregar
document.addEventListener('DOMContentLoaded', () => {
    loadSavedLanguage();
    
    // Fecha dropdown ao clicar fora
    document.addEventListener('click', (e) => {
        const dropdown = document.getElementById('langDropdown');
        const btn = document.getElementById('langBtn');
        if (dropdown && btn && !btn.contains(e.target) && !dropdown.contains(e.target)) {
            dropdown.classList.add('hidden');
        }
    });
});

// Função para alternar dropdown
function toggleLangDropdown() {
    const dropdown = document.getElementById('langDropdown');
    if (dropdown) {
        dropdown.classList.toggle('hidden');
    }
}