# Servidor web python lab
______________________________

O seguinte projeto foi feito pelos alunos Leonardo Souza Leite, Mariana dos Santos Cardoso e Pedro França Moreira para a disciplina de Redes de Computadores mestrada pelo professor Iguatemi E. Fonseca.

O projeto consiste em um web servidor feito em python que é continuamente incrementado com novas funcionalidades. A ideia do projeto foi tirada do [site do escritor Kurose](https://gaia.cs.umass.edu/kurose_ross/) e os incrementos implementados são as atividades extras dadas pelo Kurose.

## WebServer.py



## WebServerMT.py

A implementação feita nessa fase foi a de um servidor **multithread**. Para isso, a função principal foi dividida em pequenas funções para um melhor planejamento e execução da tarefa. 
Ao invés da função ter de terminar toda a criação do server, busca e leitura do arquivo, atendimento da requisição e então responder em arquivo HTTP para então ser liberado para receber outra conexão, o server não precisa esperar a resposta ser enviada para estabelecer outra conexão e criação de thread. 
