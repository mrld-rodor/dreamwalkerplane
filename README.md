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

<h2>Autenticação Admin</h2>

<p>O login administrativo agora aplica limite específico de tentativas e aceita preferencialmente senha com hash via <code>ADMIN_PASSWORD_HASH</code>. A variável <code>ADMIN_PASSWORD</code> continua funcionando apenas como fallback de compatibilidade.</p>

<p>Para gerar um hash compatível, use:</p>

<pre><code>/home/rodorxes/mrld/Projects/dreamwalkerplane_V2/.venv/bin/python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('SUA_SENHA'))"</code></pre>

<p>Depois configure:</p>

<ul>
	<li><code>ADMIN_USERNAME=seu_usuario</code></li>
	<li><code>ADMIN_PASSWORD_HASH=hash_gerado</code></li>
</ul>

<p>O valor em <code>ADMIN_PASSWORD</code> deve ser removido do ambiente assim que a migração para hash estiver concluída.</p>
