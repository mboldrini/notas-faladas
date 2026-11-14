# Notas Faladas

---

## 🧩 Situação

Estudar pelo tablet — lendo artigos, livros, PDFs — é produtivo. O problema é que ideias surgem no meio disso, e digitar no tablet é lento e chato o suficiente para quebrar o raciocínio. Falar é natural. Falar é rápido.

O Obsidian já fazia parte da rotina diária para organizar notas, referências e pensamentos. Era o destino certo para essas ideias — só faltava uma ponte entre o que era falado no tablet e o que aparecia no Obsidian no PC.

---

## ⚠️ Complicação

A alternativa eram post-its físicos. Eles se perdiam, ficavam espalhados, e a transferência para o PC nunca acontecia no momento certo. O resultado: ideias que pareciam importantes na hora sumiam antes de virar alguma coisa.

O gargalo não era a falta de ideias — era a fricção entre capturá-las e organizá-las.

---

## ✅ Resolução

**Notas Faladas** é um serviço que roda silenciosamente em background no Windows.

O fluxo é simples:

1. No tablet (via Obsidian mobile), você grava um áudio e embute no arquivo `notas faladas.md` com a sintaxe `![[arquivo.m4a]]`
2. A cada 30 minutos, o serviço verifica esse arquivo automaticamente
3. Cada áudio encontrado é transcrito localmente (sem internet, usando Whisper)
4. O embed é substituído pelo texto transcrito no próprio `.md`
5. O áudio é movido para uma pasta de arquivamento

Quando você senta no PC, a transcrição já está lá — pronta para organizar como quiser.

---

## 🚀 Instalação

### Pré-requisitos

- Python 3.10+
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
- Windows (o agendamento usa o Task Scheduler)

### Passos

**1. Clone o repositório**
```
git clone <repo-url>
cd Notas-Faladas
```

**2. Crie e ative um ambiente virtual**
```
python -m venv venv
venv\Scripts\activate
```

**3. Instale as dependências**
```
pip install faster-whisper
```

> Para usar GPU (NVIDIA), instale também os pacotes CUDA correspondentes à sua versão do driver. O serviço detecta automaticamente e cai para CPU se a GPU falhar.

**4. Configure o `config.json`**

Edite o arquivo `config.json` antes de registrar o serviço (veja a seção de configuração abaixo).

**5. Registre a tarefa agendada**
```
powershell -ExecutionPolicy Bypass -File setup.ps1
```

Isso cria uma tarefa no Windows Task Scheduler que roda o transcriber a cada 30 minutos, sem abrir janela.

---

## ⚙️ Configuração

Todas as opções ficam em `config.json` na raiz do projeto:

```json
{
  "vault_dir": "E:\\SeuVault\\Pasta",
  "notas_faladas_file": "notas faladas.md",
  "audios_transcritos_dir": "Audios-Transcritos",
  "log_file": null,
  "whisper_model": "large-v3",
  "language": "pt",
  "beam_size": 5,
  "cpu_threads": null
}
```

| Chave | Descrição | Padrão |
|---|---|---|
| `vault_dir` | Caminho absoluto para a pasta do vault Obsidian | — |
| `notas_faladas_file` | Nome do `.md` que será monitorado (relativo ao vault) | `notas faladas.md` |
| `audios_transcritos_dir` | Pasta para onde os áudios processados serão movidos (relativo ao vault) | `Audios-Transcritos` |
| `log_file` | Caminho absoluto para o arquivo de log. `null` = pasta do script | `null` |
| `whisper_model` | Modelo Whisper a usar. Opções: `tiny`, `base`, `small`, `medium`, `large-v3` | `large-v3` |
| `language` | Idioma dos áudios para transcrição | `pt` |
| `beam_size` | Qualidade vs velocidade (maior = mais preciso, mais lento) | `5` |
| `cpu_threads` | Threads usadas no modo CPU. `null` = detecta automaticamente | `null` |

> **Nota sobre modelos:** `large-v3` oferece a melhor precisão, mas é mais pesado. Para máquinas mais modestas, `medium` ou `small` são boas alternativas.

---

## 🔄 Como funciona

```
[Tablet - Obsidian Mobile]
  └── Grava áudio → embute no "notas faladas.md" como ![[audio.m4a]]

[Windows - Task Scheduler]
  └── A cada 30 min → executa transcriber.py (sem janela)
        ├── Lê "notas faladas.md"
        ├── Encontra embeds de áudio pendentes
        ├── Busca o arquivo de áudio no vault
        ├── Transcreve com Whisper (GPU se disponível, CPU como fallback)
        ├── Substitui ![[audio.m4a]] pelo texto transcrito
        └── Move o áudio para "Audios-Transcritos/"

[PC - Obsidian Desktop]
  └── Abre "notas faladas.md" → transcrição já está lá
```

---

## 📋 Monitorando

Para ver o log em tempo real:
```
Get-Content .\transcriber.log -Tail 30 -Wait
```

Para rodar manualmente (fora do agendamento):
```
venv\Scripts\python.exe transcriber.py
```

Para remover a tarefa agendada:
```
Unregister-ScheduledTask -TaskName "NotasFaladas-Transcriber" -Confirm:$false
```

---

## 🏷️ Tags
`#Obsidian` `#Whisper` `#Transcrição` `#Produtividade` `#Windows` `#Automação`
