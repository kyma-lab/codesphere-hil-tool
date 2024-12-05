import DocumentationTopic from "$lib/DocumentationTopic";

/* contains the textual content for the help page, and also defines its structure (at the bottom) */


let intro = new DocumentationTopic(
	'Das Tool',
	'GerPS-HIL ist ein Tool zur Annotation von Texten im Kontext der Normenanalyse. GerPS-HIL steht für "German Public Services - Human-in-the-Loop". Es ist für die Verwendung in der Verwaltung ausgelegt und bietet eine benutzerfreundliche Oberfläche für die Annotation von Texten. Dabei werden KI-generierte Vorschläge für die Annotationen gemacht, die von Benutzenden überprüft und gegebenenfalls korrigiert werden können. Auf diese Weise werden die Vorschläge kontinuierlich verbessert und die Genauigkeit der Annotationen erhöht. Die Annotation von Handlungsgrundlagen ist ein wichtiger Schritt auf dem Weg zur Digitalisierung der Prozesse. Bei dem Tool handelt es sich um einen Prototyp, der im Rahmen eines Forschungsprojekts entstanden ist. Die Komponenten zur Prozessmodellierung und Suche sind in frühen Testphasen. Kernfunktion des Tools ist die intelligente Unterstützung der Nutzenden bei der initialen Normenanalyse.',
	[]
);

let intro_p2 = new DocumentationTopic(
	'Warum Normenanalyse?',
	'Ziel der Normenanalyse ist es, relevante Textpassagen in Handlungsgrundlagen zu identifizieren und damit die Grundlage für die Ableitung von Verwaltungsprozessen (konkrete Verwaltungsverfahren) zu schaffen. Diese Verwaltungsprozesse sind ein zentrales Element im Prozess der Digitalisierung der Verwaltung. Für diese Aufgabe ist die Verwaltung selbst zuständig. Das Tool ist deshalb speziell für die Verwendung innerhalb der Verwaltung konzipiert.',
	[]
);

let made_by_and_for = new DocumentationTopic(
	'Entwickler',
	'GerPS-HIL wurde im Canarėno Projekt von der openDVA Arbeitsgruppe an der Friedrich Schiller Universität Jena entwickelt. Die Entwicklung ist Teil eines Forschungsprojekts, das darauf abzielt, die Normenanalyse zu unterstützen.',
	[]
);

let login = new DocumentationTopic(
	'Einloggen',
	'Um das Tool zu nutzen, benötigen Sie einen Zugang. Diesen können Sie bei Ihrem Administrator beantragen. Um sich einzuloggen, folgen Sie diesen Schritten:',
	[
		'Wenn Sie nicht eingeloggt sind, öffnet sich beim Aufruf der Tool-Seite automatisch die Login-Seite.',
		'Geben Sie Ihren Benutzernamen und Ihr Passwort ein.',
		'Klicken Sie auf "Login".'
	]
);

let dashboard_component = new DocumentationTopic(
	'Dashboard',
	'Nach dem Einloggen gelangen Sie zu Ihrem Dashboard. Hier können Sie folgendes tun:',
	[
		'Option A: Dokumente (pdf, txt) hochladen, um sie zu annotieren.',
		'Option B: Suche nutzen, um Dokumente aus der im Tool hinterlegten Datenbank zu finden.',
		'Achtung: Aktueller Arbeitsstand im Annotationseditor geht verloren, wenn Sie neue Dokumente auswählen bzw. hochladen.',
		'Nach Auswahl der Handlungsgrundlagen ("Upload"-Button) werden Sie automatisch in den Annotationseditor weitergeleitet. Dort können Sie die Normenanalyse durchführen und anschließend das Prozessmodell erstellen.'
	]
);

let database_component = new DocumentationTopic(
	'Datenbank',
	'Das Tool beinhaltet eine Sammlung von Gesetzestexten, die von gesetze-im-internet.de gesammelt wurden. Diese können von den Suchergebnissen direkt als Handlungsgrundlage in die Normenanalyse übernommen werden. Die Datenbankinhalte sind aktuell nicht formatiert und variieren in ihrer Qualität. Weiterhin werden bei jeder Suche nur die ersten 10 Ergebnisse angezeigt. Es handelt sich hierbei um ein Feature, das noch in der Entwicklung ist.',
	[]
);

let search_component = new DocumentationTopic(
	'Suche',
	'Das Tool gibt Ihnen zwei verschiedene Möglichkeiten, die Datenbank zu durchsuchen. Die gewöhnliche Suche sucht nach textueller Übereinstimmung zwischen ihrem Suchbegriff und den Dokumenten in der Datenbank. Die semantische Suche verbessert die Genauigkeit und Relevanz der Suchergebnisse, indem sie den Kontext und die Bedeutung hinter Ihren Anfragen versteht.',
	[
		'Sie können die Suche über das Eingabefeld auf dem Dashboard oder der Suche-Seite starten.',
		'Die Suchergebnisse sind nach Relevanz sortiert und können durch einen Klick "ausgeklappt" werden, um mehr Details anzuzeigen.',
		'Wählen Sie die relevanten Ergebnisse aus ("Hinzufügen"-Button) und sie erscheinen auf der rechten Seite als Liste.',
		'Klicken Sie auf "Upload" an der linken Seite neben der Liste der ausgewählten Dokumente, um die Handlungsgrundlagen in den Annotationseditor zu laden.'
	]
);

let annotation_component = new DocumentationTopic(
	'Annotationseditor',
	'Der Annotationseditor dient dem einfachen Annotieren von Dokumenten im Kontext der Normenanalyse. Annotationen können über eine einfache Point-and-Click-Mechanik neu erstellt oder verändert werden. Die zur Verfügung stehenden Annotations-Klassen sind vorgegeben und an der rechten Seite erläutert. Bei der Annotation ist es sinnvoll, einem fixen Annotationsschema zu folgen. Wenn mehrere Dokumente in den Editor geladen wurden, kann mit dem Dokumentenauswahlfenster das anzuzeigende Dokument ausgewählt werden (linke Seite). Links von dem Dokumentenauswahlfenster wird der Änderungsverlauf angezeigt. Jede Änderung kann einzeln rückgängig gemacht werden. Mehr Informationen zu den einzelnen Funktionen sind in der gesonderten Sektion zum Annotationseditor zu finden.',
	[]
);

let process_component = new DocumentationTopic(
	'Prozessmodellierer',
	'In diesem Schritt kann unter Zuhilfenahme des annotierten Texts ein BPMN-Diagramm erstellt werden. Dabei können Sie zwischen drei verschiedenen Ansichten wechseln. Erstellte Prozessdiagramme können über den "Download"-Button unten links heruntergeladen werden. Durch die gleichzeitige Bedienung des Mausrads und der STRG-Taste kann im Modellierer herein- und herausgezoomed werden. Durch einen Klick auf den "Speichern"-Button wird der aktuelle Arbeitsfortschritt lokal im Browser gespeichert. Der Button mit dem "Mülltonnen"-Symbol löscht den aktuellen Arbeitsfortschritt. Beim Wechsel der Ansicht wird der aktuelle Arbeitsfortschritt automatisch gespeichert und bleibt erhalten.',
	[]
);

let process_component_remark = new DocumentationTopic(
	'',
	'Aktuell unterstützt das Modellierungsmodul nicht die Besonderheiten des FIM-BPMN, sondern nur reguläres BPMN 2.0.',
	[]
);

let additional_information_pane = new DocumentationTopic(
	'Zusätzliche Informationen',
	'Rechts neben der Auswahl der aktuellen Ansicht finden Sie einen grauen Button mit dem Sie sich in einem Popup-Fenster eine Liste der über alle Dokumente hinweg annotierten Datenfelder, Dokumente und Bedingungen anzeigen lassen können. Damit können Sie am Ende kontrollieren, ob alle Dokumente und Datenfelder in Ihrem Prozessmodell vorkommen.',
	[
		'Auf den Button klicken, um das Popup-Fenster zu öffnen.',
		'Die Informationen werden in einer Liste angezeigt.',
		'Sie können die aktuell ausgewählte Klasse ändern.',
		'Außerhalb des Popup-Fensters klicken, um es zu schließen.'
	]
);

let annotation = new DocumentationTopic(
	'',
	'Dieser Abschnitt enthält mehr Informationen zu einzelnen Funktionen des Annotationseditors. Auf dem linken Teil der Seite ist eine Historie der zuletzt vorgenommenen Änderungen sichtbar. Auf dem rechten Teil der Seite sind Informationen zu den verschiedenen Annotationsklassen sichtbar. Im mittleren, zentralen Teil der Website ist der Text des Dokuments sichtbar. Hier können Anmerkungen hinzugefügt, bearbeitet oder gelöscht werden.',
	[]
);

let annotation_update_class = new DocumentationTopic(
	'Aktualisierung der annotierten Klasse',
	'So können Sie die Klasse ändern, die einem Textsegment zugeordnet ist:',
	[
		'Klicken Sie auf die Annotation, dessen Klasse Sie aktualisieren möchten.',
		'Wählen Sie im Popup-Fenster die gewünschte neue Klasse aus.'
	]
);

let annotation_update_boundary = new DocumentationTopic(
	'Aktualisierung des Textumfangs einer Annotation',
	'So können Sie den Text, der zu einer Annotation gehört, verändern:',
	[
		'Klicken Sie auf die Annotation, dessen Klasse Sie aktualisieren möchten.',
		'Entfernen Sie im Popup-Fenster die aktuelle Annotation.',
		'Markieren Sie das Textsegment, das die neue Annotation umfassen soll.',
		'Wählen Sie im Popup-Fenster die gewünschte neue Klasse aus.'
	]
);

let annotation_delete = new DocumentationTopic(
	'Entfernen von Annotationen',
	'Wenn eine Anmerkung falsch oder unnötig ist, können Sie sie so löschen:',
	[
		'Finden Sie die Annotation, die Sie löschen möchten.',
		'Entfernen Sie im Popup-Fenster (rotes X) die aktuelle Annotation.'
	]
);

let annotation_add = new DocumentationTopic(
	'Erstellen neuer Annotationen',
	'So können Sie Annotationen manuell hinzufügen:',
	[
		'Markieren Sie das Textsegment, das Sie annotieren möchten.',
		'Wählen Sie die gewünschte Klasse aus den verfügbaren Optionen.',
		'Falls Sie alle identischen (nicht bereits annotierten) Textsegmente gleichzeitig annotieren möchten, können Sie auf den "Alle" Button klicken.'
	]
);

let annotation_change_doc = new DocumentationTopic(
	'Ändern des aktuellen Dokuments',
	'Wenn mehrere Dokumente in den Editor geladen wurden, können Sie das aktuell angezeigte Dokument so ändern:',
	[
		'Gegebenenfalls ist es nötig, dass Sie zunächst das Dokumentenauswahlfenster maximieren müssen, um es zu sehen (kleiner runder blauer Button mit Pfeil-Icon auf der linken Seite).',
		'Klicken Sie auf das Dokumentenauswahlfenster auf der linken Seite.',
		'Wählen Sie das gewünschte Dokument aus.',
		'Optional: Minimieren Sie das Dokumentenauswahlfenster, um mehr Platz für den Text zu haben.'
	]
);

let annotation_confirm = new DocumentationTopic(
	'Bestätigen der Annotationen',
	'Wenn Sie mit der Normenanalyse fertig sind, können Sie die Annotationen so bestätigen:',
	[
		'Klicken Sie auf den blauen "Annotationen bestätigen"-Button oben rechts.',
		'Bestätigen Sie im Dialogfenster erneut den gewünschten Vorgang.',
		'Sie werden automatisch zum Prozessmodellierer weitergeleitet.'
	]
);

let annotation_undo = new DocumentationTopic(
	'Rückgängig machen von Änderungen',
	'Wenn Sie eine Änderung rückgängig machen möchten, können Sie dies so tun:',
	[
		'Hinweis: Sie können für jede Änderung Details anzeigen lassen.',
		'Klicken Sie bei der gewünschten Änderung auf das "Rückgängig"-Symbol (kreisförmig ausgerichteter Pfeil) in der Historie auf der linken Seite.',
		'Wiederholen Sie den Vorgang, um weitere Änderungen rückgängig zu machen.'
	]
);

let ablauf_intro = new DocumentationTopic(
	'',
	'In den meisten Fällen werden Sie die Module in der folgenden Reihenfolge durchlaufen:',
	[]
);

let annotationstep = new DocumentationTopic(
	'Annotation',
	'Die Annotation beginnt mit dem Hochladen von Handlungsgrundlagen, die dann von unseren maschinellen Lernalgorithmen verarbeitet werden, um Ihnen nützliche Vorschläge für Annoationen bereitzustellen. Sie können PDF- oder TXT-Dokumente hochladen. Das Tool extrahiert automatisch den Text. ',
	[
		'Hochladen eines Dokuments: Navigieren Sie zum Hochladebereich und wählen Sie das Dokument aus, das Sie annotieren möchten. Sie können mehrere Dokumente wählen, nacheinander oder gleichzeitig. Jedes Dokument darf maximal 10 Megabyte groß sein. Die Datentypen PDF und TXT dürfen gemischt auftreten. Klicken Sie auf "Upload".',
		'KI-Unterstützung: Das Dokument wird auf unserem Server von den von uns trainierten KI-Modellen verarbeitet, um Annotationsvorschläge zu erzeugen. Das kann, je nach Größe des Dokuments, einen Moment dauern.',
		'Überprüfen und Bearbeiten: Sie werden automatisch zum Annotationseditor weitergeleitet. Dort können Sie, unterstützt durch die Annotationsvorschläge, die Normenanalyse durchführen.',
		'Fertig?  Wenn Sie mit der Normenanalyse fertig sind, können Sie über den blauen "Annotationen bestätigen"-Button zur Prozessmodellierung übergehen.'
	]
);

let process = new DocumentationTopic(
	'Prozessmodellierung',
	'Der Prozessmodellierer dient der Prozessmodellierung. Ziel der Prozessmodellierung ist es, basierend auf den Handlungsgrundlagen ein Prozessdiagramm zu erstellen, welches das Verwaltungsverfahren für den gewählten Prozess abbildet. In diesem Modul stehen drei Ansichten zur Verfügung, zwischen denen Sie nach Belieben wechseln können. Das fertig modellierte BPMN-Diagramm kann durch einen Klick auf den "Download"-Button heruntergeladen werden. Es kann später per Drag-and-Drop wieder importiert werden.',
	[]
);

let process_disclaimer = new DocumentationTopic(
	'',
	'Aktuell unterstützt das Modellierungsmodul nicht die Besonderheiten des FIM-BPMN, sondern nur reguläres BPMN 2.0. Die Modellierung von BPMN Prozessen erfolgt hier horizontal, nicht vertikal.',
	[]
);

let process_tipps = new DocumentationTopic(
	'Tipps',
	'Hier finden Sie einige Tipps zur Benutzung des Prozessmodellierers:',
	[
		'Um die Ansicht auf dem Canvas zu bewegen, halten Sie die Maustaste gedrückt und ziehen Sie in die gewünschte Richtung.',
		'Sie sollten regelmäßig den "Speichern"-Button nutzen, um ihren Zwischenstand zwischenzuspeichern.',
		'Mit STRG + Mausrad können Sie herein- und herauszoomen.',
		'Der "Mülltonnen"-Button oberhalb der Werkzeug-Palette löscht das aktuelle Diagramm.',
		'Der aktuelle Arbeitsfortschritt wird beim Wechsel der Ansichten automatisch gespeichert.',
		'Elemente durch einen Klick auf das kleine Werkzeug-Symbol nach der Platzierung bearbeitet werden.'
	]
);

let process_views = new DocumentationTopic(
	'Ansichten',
	'Es gibt drei Ansichten, die Sie verwenden können:',
	[
		'Text-Ansicht: In dieser Ansicht können Sie sich die Handlungsgrundlagen inklusive der vorgenommenen Annotationen erneut durchlesen.',
		'BPMN-Ansicht: In dieser Ansicht können Sie den Prozess modellieren.',
		'Kombinierte Ansicht: In dieser Ansicht können Sie den Prozess modellieren und haben gleichzeitig die Möglichkeit, den annotierten Text zu referenzieren (anzusehen).'
	]
);

let process_step = new DocumentationTopic(
	'Prozessmodellierung',
	'Diesen Schritt sollten Sie durchlaufen, nachdem Sie die Normenanalyse abgeschlossen haben. Die annotierten Dokumente werden nach Bestätigen der Annotationen im Annotationseditor automatisch in die Text-Ansicht des Prozessmodellierers geladen, und die Ansicht wechselt automatisch zu diesem Schritt.',
	[
		'Wählen Sie die gewünschte Ansicht und das aktuell relevante Dokument.',
		'Modellieren Sie den Prozess.',
		'Speichern Sie regelmäßig.',
		'Laden Sie, falls gewünscht, das fertige Prozessmodell im BPMN Format herunter.'
	]
);

let video_component = new DocumentationTopic(
	'Video',
	'Ein Video zur Verwendung des Tools finden Sie unten:',
	[]
);


// the structure of the help page
// the html is generated by iterating over the topics and subtopics



// the frequently asked questions

let qa02 = new DocumentationTopic(
	'Wie kann ich ein lokal im .bpmn vorhandenes BPMN Prozessmodell bearbeiten?',
	'Um ein bereits bestehendes Prozessmodell zu bearbeiten, können Sie es per Drag-and-Drop in den Prozessmodellierer ziehen. Dort können Sie es dann bearbeiten. Manchmal funktioniert der Upload per Drag-and-Drop nicht auf Anhieb.',
	[]
);

let qa03 = new DocumentationTopic(
	'An wen kann ich mich bei Fragen oder Problemen wenden?',
	'Bitte nutzen Sie die "Kontakt" Schaltfläche in der Fußleiste.',
	[]
);

let qa04 = new DocumentationTopic(
	'Die Website funktioniert nicht richtig. Was kann ich tun?',
	'Falls es bei der Nutzung des Tools zu Problemen kommt, empfehlen wir die Seite zu aktualisieren (F5 oder Aktualisieren-Button in der Adressleiste). Hilft das nicht, folgen Sie den folgenden Schritten:',
	[
		'Aktualisieren Sie die Seite.',
		'Klicken Sie auf das Zahnrad-Symbol oben rechts.',
		'Klicken Sie auf "Cache löschen" (Achtung: löscht zwischengespeicherten Arbeitsstand!).',
		'Aktualisieren Sie die Seite erneut.',
		'Optional: Wir empfehlen die Nutzung von Google Chrome oder Mozilla Firefox.'
	]
);

let qa05 = new DocumentationTopic(
	'Wie kann ich die Sprache der Website ändern?',
	'Das ist aktuell leider noch nicht möglich.',
	[]
);

let qa06 = new DocumentationTopic(
	'Wie kann ich nachträglich ein weiteres Dokument zum Annotationseditor oder Prozessmodellierer hinzufügen?',
	'Das ist aktuell leider noch nicht möglich. Stattdessen könnten Sie den gesamten Vorgang neu starten und den neuen Dokumentensatz hochladen, oder das Tool in einem zusätzlichen Fenster neu aufrufen und dort das neue Dokument separat hochladen und bearbeiten.',
	[]
);

let qa07 = new DocumentationTopic(
	'Kann ich, wenn ich im Schritt der Prozessmodellierung bin, noch die Annotationen ändern?',
	'Ja, Sie können über die Navigationsleiste zurück in den Annotationseditor wechseln, die Annotationen ändern und erneut bestätigen. Achtung: Dabei wird der Inhalt des Prozessmodellierers (Diagramm) gelöscht.',
	[]
);


/* the structure that will be passed to the help page */

export let topics = {
	Kontext: [intro, intro_p2, made_by_and_for],
	'Erste Schritte': [video_component, login, dashboard_component, search_component],

	Module: [database_component, annotation_component, process_component, process_component_remark],
	Annotationseditor: [
		annotation,
		annotation_update_class,
		annotation_update_boundary,
		annotation_delete,
		annotation_add,
		annotation_change_doc,
		annotation_undo,
		annotation_confirm
	],
	Prozessmodellierer: [
		process,
		process_disclaimer,
		process_tipps,
		process_views,
		additional_information_pane
	],
	Beispielablauf: [ablauf_intro, annotationstep, process_step]
};


export let questions = [qa02, qa04, qa05, qa06, qa07, qa03];