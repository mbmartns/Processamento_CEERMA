Há 3 rotinas na Versão de Laboratório da Pasta Rotina 2.0

A lab_ctd_atualizada.py é uma rotina de laboratório em que há o processamento das estações determinadas e toda a criação da arquitetura das pastas;
A rotina_pos_process.py é uma rotina de pós-processamento, ou seja, os dados já passaram pela a etapa da rotina anterior, a ideia dessa rotina é criar mais duas pastas em que os dados (arquivos cnv) são colocados em uma das pastas e há o tratamento na outra;
A pos_process_com_flag1 é uma atualização dessa rotina, mas, ao tratar os dados, coloca algumas flags de condutividade e temperatura para indicar a qualidade dos dados.

Na pasta de Versão Embarcada, há dois arquivos que vão fazer o processamento das estações de uma maneira adequada para um operador que esteja embarcado.
Para isso, há dois arquivos:

config_ctd.py, que deixa configurado a arquitetura de pastas, tal como o batch a ser usado;
process_ctd_embarcado.py realiza o processamento das estações desejadas.

Essas rotinas facilitam o processamento em um ambiente em que os dados estão ainda sendo adquiridos.