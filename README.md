<h1>DreamWalker Plane</h1>

<p>Portal onírico</p>

<h2>Configuração de email no Render</h2>

<p>O projeto usa envio por API HTTP para evitar o bloqueio de portas SMTP em instâncias Free do Render.</p>

<p>Configure as variáveis abaixo nas Config Vars:</p>

<ul>
	<li><code>RESEND_API_KEY</code>: chave da API do Resend</li>
	<li><code>EMAIL_SENDER</code>: remetente validado no Resend, por exemplo <code>DreamWalker Plane &lt;contato@seudominio.com&gt;</code></li>
	<li><code>EMAIL_RECEIVER</code>: destinatário que receberá os contatos do formulário</li>
	<li><code>EMAIL_API_TIMEOUT</code>: opcional, timeout em segundos, padrão <code>10</code></li>
</ul>
