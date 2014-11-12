=====================
python-passaporte-web
=====================

.. image:: https://travis-ci.org/myfreecomm/python-passaporte-web.png?branch=master
        :target: https://travis-ci.org/myfreecomm/python-passaporte-web


Sobre o Passaporte Web
----------------------

O Passaporte Web é um ecossistema de aplicações corporativas que disponibiliza uma série de funcionalidades para
simplificar a implementação, operação e comercialização de suas aplicações; com o objetivo de possibilitar que você
se preocupe somente com o desenvolmento das funções diretamente relacionadas aos objetivos de sua aplicação.

Nosso objetivo é construir uma comunidade de desenvolvedores e aplicações de altíssima qualidade.

O Passaporte Web oferece:
    - Mecanismos de cadastro de usuários, autenticação e controle de acesso centralizado;
    - Ferramentas para gestão de usuários, vendas, pagamentos, aplicações e controle de acesso aos sistemas e às APIs;
    - Sistema de venda de acesso às aplicações, com suporte a múltiplos meios de pagamento e cobrança recorrente;
    - Mecanismos para simplificar a integração entre aplicações do ecossistema;
    - Ambientes de homologação (sandbox) para auxiliar o desenvolvimento e evolução de sua aplicação;


Exemplo de utilização
---------------------

.. code-block:: python

    from passaporte_web.main import Application

    my_application = Application(
        host='https://sandbox.app.passaporteweb.com.br',
        token='qxRSNcIdeA',
        secret='1f0AVCZPJbRndF9FNSGMOWMfH9KMUFfF',
    )

    # Cadastrar um usuário
    user_data = {
        'first_name': 'José',
        'last_name': 'Ninguém',
        'email': 'jose.ninguem@example.test',
        'password': 'wmvgCW1WWa',
        'password2': 'wmvgCW1WWa',
        'tos': True,
    }
    new_user = my_application.users.create(**user_data)

    # Ler e atualizar perfil do usuário
    user_profile = new_user.profile
    user_profile.bio = u'Eu sou o usuário do exemplo de utilização.'
    user_profile.nickname = 'johndoe'
    user_profile = user_profile.save()

    # Criar uma conta para o usuário na aplicação
    app_account = new_user.accounts.create(
        name=u'Conta do usuário {0.email}'.format(new_user),
        plan_slug='test-plan',
        expiration=None,
    )


    # Listar as contas associadas a esta aplicação
    for account in my_application.accounts.all():
        print 'Account {0.name} with uuid {0.uuid} e plano {0.plan_slug}'.format(account)
