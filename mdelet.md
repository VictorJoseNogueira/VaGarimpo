
2026-05-23 07:02:30,775 - scrapper - INFO - plataforma de tokenização com smart contracts erc-20 e painel admin
2026-05-23 07:02:30,775 - scrapper - WARNING - visão geral
empresa do setor de tecnologia financeira busca profissional para desenvolver uma plataforma web completa de tokenização, composta por três camadas integradas: (1) conjunto de smart contracts em rede evm-compatible, (2) backend de orquestração e api, e (3) frontend web com painel administrativo e portal do titular.
o projeto exige profissional com experiência comprovada e verificável em desenvolvimento de smart contracts solidity em produção, além de stack web moderno. não é projeto para generalistas nem para profissionais que estão "aprendendo solidity no projeto". o contratado entregará uma plataforma funcional, testada e auditável.
a contratação prioriza velocidade de execução com qualidade não negociável. o contratante valoriza profissionais que entregam rápido sem comprometer segurança ou cobertura de testes. propostas com prazos irrealisticamente curtos serão desconsideradas, pois indicam desconhecimento da complexidade real.
---
escopo técnico - camada 1: smart contracts
conjunto de três contratos interligados:
- contrato de emissão (token contract)
padrão erc-20 estendido, em rede evm-compatible a definir no marco 1 (polygon, bsc, base ou arbitrum candidatas).
funções: mint controlado, burn, transfer com whitelist, pause/unpause, ownership multisig.
whitelist de carteiras autorizadas (compliance kyc off-chain).
eventos completos para auditoria externa.
limite de supply parametrizável.

- contrato de tesouraria (vault contract)
recebe depósitos em usdt (erc-20 ou trc-20, conforme rede final).
emite tokens proprietários proporcionalmente ao nav atualizado.
fila de saque programado com janela t+n dias configurável.
multisig para movimentações acima de threshold.
reserva técnica mínima parametrizável.
circuit breaker (pause emergencial).
função redeem com verificação de saldo da reserva.

- contrato de distribuição (distribution contract)
cálculo de valores periódicos por holder.
lógica configurável: taxa diária, capitalização mensal, ciclos parametrizáveis.
snapshot de holders no fechamento de cada ciclo.
histórico on-chain auditável.
função claim individual.

padrões de segurança obrigatórios:
- openzeppelin contracts como base.
- reentrancyguard em todas as funções de movimentação de valor.
- checks-effects-interactions pattern.
- pull-over-push para retiradas.
- accesscontrol com roles separadas (admin, minter, pauser, treasury).
---
escopo técnico - camada 2: backend
api rest ou graphql responsável por orquestração off-chain:
- autenticação e autorização (jwt, refresh tokens, rbac).
- onboarding de usuário com captura de dados kyc (integração com provedor a definir, ou mock inicial).
- gestão de carteiras: opção de custódia interna ou integração com carteira self-custody (metamask, walletconnect) - escolha técnica a ser justificada pelo contratado no marco 1.
- conversão pix - usdt via integração com gateway/exchange (sandbox inicial; produção fora de escopo desta contratação).
- listener de eventos on-chain (subscribers via websocket de nó rpc ou alchemy/infura).
- indexação de transações e snapshots em banco postgresql.
- cálculo off-chain consolidado de saldos e rendimentos por usuário.
- geração de relatórios em pdf (extrato consolidado por titular).
- endpoints administrativos para operação da tesouraria.

stack esperado:
- node.js (nestjs, express, fastify) ou python (fastapi, django).
- postgresql como banco principal.
- redis para fila e cache.
- ethers.js ou web3.py para integração on-chain.
- docker para containerização.
- testes automatizados (jest, pytest, vitest) com cobertura mínima de 80%.
---
escopo técnico - camada 3: frontend
aplicação web responsiva com dois escopos distintos:
- painel administrativo (interno)
- dashboard com métricas operacionais (aum, holders, ciclo atual, posição da tesouraria).
- gestão de usuários e carteiras.
- aprovação dual para operações sensíveis (mint, burn, ajuste de nav).
- visualização de fila de redemption.
- logs de auditoria.
- configuração de parâmetros (taxas, ciclos, threshold de multisig).
- relatórios exportáveis (pdf, excel).

- portal do titular (público logado)
- onboarding com kyc.
- visualização do saldo de tokens.
- histórico de transações.
- extrato consolidado mensal.
- solicitação de novo aporte (depósito usdt/pix).
- solicitação de saque (entra na fila programada).
- documentos disponíveis para download.

stack esperado:
- react (next.js 14+) ou vue 3 (nuxt).
- typescript obrigatório.
- tailwindcss + shadcn/ui ou equivalente.
- react query / tanstack query para state server.
- componentização clara, design system mínimo.
- suporte responsivo desktop-first com adaptação mobile.
---
entregáveis consolidados
- repositório git privado único com monorepo organizado (/contracts, /backend, /frontend, /docs).
- código de smart contracts com 90% de cobertura de testes (hardhat ou foundry).
- backend com 80% de cobertura.
- documentação técnica em markdown contendo: arquitetura geral, erd do banco, diagramas de sequência dos principais fluxos, manual de deploy.
- scripts de deploy parametrizáveis para testnet e ambiente de homologação.
2026-05-23 07:02:30,775 - scrapper - INFO - Iniciando chamada ao agente
2026-05-23 07:02:30,776 - scrapper - DEBUG - run_agent: tamanho do input=5309
2026-05-23 07:02:33,386 - scrapper - CRITICAL - {
  "status": "Compatível",
  "match_percentage": 90,
  "strengths": [
    "Experiência em desenvolvimento de smart contracts em produção",
    "Domínio em Solidity",
    "Conhecimento em stack web moderno",
    "Experiência em desenvolvimento de sistemas completos",
    "Conhecimento em Node.js, Python, PostgreSQL, Redis, Docker, Jest, Pytest, Vitest",
    "Conhecimento em React, Vue.js, Next.js, Nuxt.js, TypeScript, Tailwindcss, Shadcn/UI"
  ],
  "weaknesses": [
    "Falta de experiência em desenvolvimento de contratos de distribuição",
    "Falta de experiência em desenvolvimento de painéis administrativos"
  ],
  "payments": "R$ 13.844,40",
  "proposal": "Olá, Equipe,\n\nVi sua busca por um desenvolvedor para desenvolver uma plataforma de tokenização com smart contracts ERC-20 e painel administrativo e meu perfil se alinha exatamente ao que você precisa. Entendi que seu principal desafio atual é desenvolver uma plataforma funcional, testada e auditável com velocidade de execução e qualidade não negociável.\n\nComo posso ajudar:\n- Desenvolvimento de smart contracts em produção: Tenho experiência em desenvolver smart contracts em produção e posso ajudar a desenvolver os contratos de emissão, tesouraria e distribuição.\n- Stack web moderno: Tenho conhecimento em stack web moderno e posso ajudar a desenvolver o backend e frontend da plataforma.\n\nPortfólio:\n- GitHub: https://github.com/VictorJoseNogueira\n- LinkedIn: https://www.linkedin.com/in/victor-nogueira-193a67256\n\nEstimativa Comercial Inicial:\n- Prazo Estimado: 12 semanas | Investimento: R$ 13.844,40.\n\nVocê pode me perguntar: Qual é a melhor abordagem para implementar a lógica de distribuição nos smart contracts?\n\nNo aguardo,\nVictor José Nogueira Santos | victorvalim1@gmail.com"