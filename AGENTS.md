# AGENTS.md

## Projekt: LoRA-Datenbank mit Webinterface

Dieses Dokument beschreibt die Agenten (Workflows, Verantwortlichkeiten und Automatisierungsschritte) für das LoRA-Datenbanksystem mit Fokus auf Upload, Verwaltung, Anzeige und Suche von LoRA-Dateien (.safetensors) samt zugehöriger Preview-Bilder.

---

## 🤖 Agentenübersicht

### 1. **Uploader-Agent**

**Aufgaben:**

* Entgegennahme von .safetensors-Dateien (einzeln oder bulk)
* Entgegennahme von Preview-Bildern im Bulk (.png/.jpg)
* Validierung: Dateinamen, Format, konsistente Zuordnung
* Speichern der Dateien im entsprechenden LoRA-Verzeichnis

**Workflow:**

1. Nutzer lädt .safetensors-Dateien + Previews hoch
2. Agent ordnet Preview-Bilder der LoRA-Datei anhand des Namens zu (oder eines JSON-Mappings)
3. Agent lässt den Metadata-Extractor-Agenten anlaufen

---

### 2. **Metadata-Extractor-Agent**

**Aufgaben:**

* Extraktion von Metadaten aus .safetensors-Dateien (Name, Dimension, Epochs, Training-Tags, etc.)
* Optional: Auslesen von eingebetteten JSON-Metadaten
* Speichern der Metadaten in der Index-Datenbank
* Tags den globalen Suchfiltern hinzufügen

**Workflow:**

1. Datei entpacken / analysieren
2. Trainingstags extrahieren (z. B. aus "clip\_tag", falls vorhanden)
3. Speichern in der LoRA-Datenbank inkl. Verlinkung zur Datei und Previews

---

### 3. **Indexing-Agent**

**Aufgaben:**

* Pflegt eine suchoptimierte Datenbank für:

  * LoRA-Name
  * Dateiname
  * Trainingstags
  * Benutzerdefinierte Tags
* Ermöglicht Suche per Name und Tag (inkl. Autovervollständigung)

**Workflow:**

1. Erhält Input vom Metadata-Extractor
2. Indexiert und aktualisiert Suchstruktur (Elasticsearch / SQLite FTS / Custom)

---

### 4. **Frontend-Agent (Gallery Viewer)**

**Aufgaben:**

* Darstellung der LoRA-Datenbank im Grid-Style (Dark Mode)
* Jedes Gridfeld:

  * Zufällig gewähltes Preview-Bild einer LoRA
  * Name der LoRA
  * Klickbar führt zur Detailansicht

**Workflow:**

1. Holt Grid-Daten aus Datenbank/API
2. Rendered dynamisch eine Vorschau-Galerie (responsive, lazy-loading)
3. Detailansicht bei Klick:

   * Galerie aller zugeordneten Previews (Bilder öffnen in neuem Tab bei Klick)
   * Metadatenanzeige
   * Download-Link zur .safetensors-Datei

---

## 🌐 Webinterface: Funktionen

| Feature                  | Beschreibung                                                |
| ------------------------ | ----------------------------------------------------------- |
| Bulk Upload              | Mehrere LoRAs und zugehörige Bilder gleichzeitig hochladbar |
| Auto-Matching            | Ordnet Previews automatisch zu LoRA-Dateien (Name/Mapping)  |
| Metadaten-Parser         | Extrahiert relevante Trainingsdaten automatisch             |
| Grid-Gallery             | Zufallsbild je LoRA, klickbar zur Detailansicht             |
| Tag-Suche & Filter       | Suche nach Name oder Trainings-Tag (Filter kombinierbar)    |
| Dark Mode UI             | Standard-Design in dunkler, kontrastreicher Darstellung     |
| Responsive               | Mobilfreundlich, skalierbar für alle Geräte                 |
| Download/Preview-Zugriff | Direkt in der Detailansicht möglich                         |

---

## ⚙️ Zukünftige Erweiterungen (Optional)

* Benutzerkonten für private / öffentliche LoRAs
* Favoriten / Bewertungssystem
* REST-API für Dritt-Integration (z. B. Inference-Skripte)
* Upload per Drag-&-Drop + Fortschrittsanzeige

---

## Hinweis zur Implementierung

* Frontend: React / Vue mit Tailwind (dark)
* Backend: Flask / FastAPI mit Celery für Metadaten- und Upload-Prozesse
* Speicherstruktur: LoRAs nach Hash oder eindeutiger ID benannt
* Bilder in dediziertem Ordner pro LoRA
* Optionaler Redis-Cache für Suchindex

---

