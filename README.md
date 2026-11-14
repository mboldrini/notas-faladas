# Notas Faladas

> 🇧🇷 [Leia em Português](README.pt-BR.md)

---

## 🧩 Situation

Studying on a tablet — reading articles, books, PDFs — is productive. The problem is that ideas come up mid-session, and typing on a tablet is slow and disruptive enough to break your train of thought. Speaking is natural. Speaking is fast.

Obsidian was already part of a daily workflow for organizing notes, references, and ideas. It was the right destination for these thoughts — the missing piece was a bridge between what was spoken on the tablet and what appeared in Obsidian on the PC.

---

## ⚠️ Complication

The fallback was physical post-its. They got lost, scattered, and the transfer to the PC never happened at the right time. The result: ideas that felt important in the moment vanished before becoming anything.

The bottleneck wasn't a lack of ideas — it was the friction between capturing them and organizing them.

---

## ✅ Resolution

**Notas Faladas** is a background service that runs silently on Windows.

The flow is straightforward:

1. On the tablet (via Obsidian mobile), record an audio and embed it in `notas faladas.md` using `![[file.m4a]]`
2. Every 30 minutes, the service checks that file automatically
3. Each audio found is transcribed locally (no internet required, using Whisper)
4. The embed is replaced by the transcribed text directly in the `.md`
5. The audio file is moved to an archive folder

By the time you sit down at the PC, the transcription is already there — ready to organize however you want.

---

## 🚀 Installation

### Prerequisites

- Python 3.10+
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
- Windows (scheduling relies on Task Scheduler)

### Steps

**1. Clone the repository**
```
git clone <repo-url>
cd Notas-Faladas
```

**2. Create and activate a virtual environment**
```
python -m venv venv
venv\Scripts\activate
```

**3. Install dependencies**
```
pip install faster-whisper
```

> To use GPU (NVIDIA), also install the CUDA packages matching your driver version. The service auto-detects and falls back to CPU if the GPU is unavailable.

**4. Configure `config.json`**

Edit `config.json` before registering the service (see the Configuration section below).

**5. Register the scheduled task**
```
powershell -ExecutionPolicy Bypass -File setup.ps1
```

This creates a Task Scheduler entry that runs the transcriber every 30 minutes with no visible window.

---

## ⚙️ Configuration

All options live in `config.json` at the project root:

```json
{
  "vault_dir": "C:\\Your\\Obsidian\\Vault",
  "notas_faladas_file": "notas faladas.md",
  "audios_transcritos_dir": "Audios-Transcritos",
  "log_file": null,
  "whisper_model": "large-v3",
  "language": "pt",
  "beam_size": 5,
  "cpu_threads": null
}
```

| Key | Description | Default |
|---|---|---|
| `vault_dir` | Absolute path to the Obsidian vault folder | — |
| `notas_faladas_file` | Name of the `.md` file to monitor (relative to vault) | `notas faladas.md` |
| `audios_transcritos_dir` | Folder where processed audio files are moved (relative to vault) | `Audios-Transcritos` |
| `log_file` | Absolute path to the log file. `null` = script folder | `null` |
| `whisper_model` | Whisper model to load. Options: `tiny`, `base`, `small`, `medium`, `large-v3` | `large-v3` |
| `language` | Language of the audio recordings | `pt` |
| `beam_size` | Quality vs. speed tradeoff (higher = more accurate, slower) | `5` |
| `cpu_threads` | Threads used in CPU mode. `null` = auto-detect | `null` |

> **Model note:** `large-v3` gives the best accuracy but is heavier. For less powerful machines, `medium` or `small` are good alternatives.

---

## 🔄 How it works

```
[Tablet - Obsidian Mobile]
  └── Record audio → embed in "notas faladas.md" as ![[audio.m4a]]

[Windows - Task Scheduler]
  └── Every 30 min → runs transcriber.py (no window)
        ├── Reads "notas faladas.md"
        ├── Finds pending audio embeds
        ├── Locates the audio file in the vault
        ├── Transcribes with Whisper (GPU if available, CPU as fallback)
        ├── Replaces ![[audio.m4a]] with the transcribed text
        └── Moves audio to "Audios-Transcritos/"

[PC - Obsidian Desktop]
  └── Opens "notas faladas.md" → transcription is already there
```

---

## 📋 Monitoring

Watch the log in real time:
```
Get-Content .\transcriber.log -Tail 30 -Wait
```

Run manually (outside the schedule):
```
venv\Scripts\python.exe transcriber.py
```

Remove the scheduled task:
```
Unregister-ScheduledTask -TaskName "NotasFaladas-Transcriber" -Confirm:$false
```

---

## 🏷️ Tags
`#Obsidian` `#Whisper` `#Transcription` `#Productivity` `#Windows` `#Automation`
