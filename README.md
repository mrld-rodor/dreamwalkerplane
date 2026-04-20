<h1>DreamWalker Plane</h1>

<p>Portal onírico</p>

<h2>Headers de segurança</h2>

<p>A aplicação envia os headers <code>X-Frame-Options</code>, <code>X-XSS-Protection</code>, <code>X-Content-Type-Options</code>, <code>Content-Security-Policy</code> e <code>Referrer-Policy</code> por padrão.</p>

<p>Para que o header <code>Strict-Transport-Security</code> apareça corretamente em produção, publique a aplicação atrás de HTTPS e configure:</p>

<ul>
	<li><code>SESSION_COOKIE_SECURE=true</code></li>
	<li><code>ENABLE_HSTS=true</code></li>
	<li><code>TRUSTED_PROXY_HOPS=1</code> quando houver um proxy reverso na frente da aplicação</li>
</ul>

<p>O HSTS não deve ser validado por scanner em HTTP local. A verificação correta é no domínio HTTPS publicado.</p>

<h2>Proteção CSRF</h2>

<p>Os formulários <code>POST</code> administrativos e públicos agora enviam um token CSRF baseado em sessão. Se o token estiver ausente ou inválido, a aplicação rejeita a submissão para evitar disparos cruzados de ações administrativas e envios indevidos de formulário.</p>
