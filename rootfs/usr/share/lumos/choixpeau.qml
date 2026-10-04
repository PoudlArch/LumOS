// Le Choixpeau — cérémonie de la Répartition, en fenêtre plein écran.
// Lancé par /usr/local/bin/choixpeau quand une session graphique et le runtime
// « qml » sont disponibles. Quand une maison est choisie, la ligne
// « LUMOS_MAISON=<maison> » est écrite sur la sortie, puis la fenêtre se ferme ;
// le script bash lit cette ligne et applique le thème. Échap = annuler.
import QtQuick
import QtQuick.Window

Window {
    id: win
    width: 1280; height: 800
    visibility: Window.FullScreen
    color: "#090612"
    title: "Le Choixpeau"

    property int etape: 0
    property int sGry: 0
    property int sSer: 0
    property int sRav: 0
    property int sPou: 0
    property string elue: ""
    readonly property string serif: "Liberation Serif"
    readonly property string or: "#d3a625"

    readonly property var questions: [
        { "q": "Au fond d'un vieux grenier, tu trouves…", "opts": [
            { "m": "serdaigle",   "t": "Un grimoire aux marges couvertes d'annotations" },
            { "m": "gryffondor",  "t": "Une épée rouillée qui semble t'attendre" },
            { "m": "poufsouffle", "t": "Une boîte de recettes écrites à la main" },
            { "m": "serpentard",  "t": "Un coffret fermé par un mécanisme ingénieux" } ] },
        { "q": "Ton terminal affiche une erreur incompréhensible. Tu…", "opts": [
            { "m": "gryffondor",  "t": "relances la commande avec sudo, on verra bien" },
            { "m": "serpentard",  "t": "trouves un contournement que personne n'avait vu" },
            { "m": "serdaigle",   "t": "lis le manuel jusqu'à comprendre pourquoi" },
            { "m": "poufsouffle", "t": "demandes de l'aide, puis notes la solution pour les suivants" } ] },
        { "q": "Ce que tu aimerais qu'on retienne de toi :", "opts": [
            { "m": "poufsouffle", "t": "Ta loyauté" },
            { "m": "serdaigle",   "t": "Ton savoir" },
            { "m": "gryffondor",  "t": "Ton courage" },
            { "m": "serpentard",  "t": "Ton ambition" } ] }
    ]
    readonly property var libelles: { "gryffondor": "Gryffondor", "serpentard": "Serpentard", "serdaigle": "Serdaigle", "poufsouffle": "Poufsouffle" }
    readonly property var couleurs: { "gryffondor": "#c0392b", "serpentard": "#2ecc71", "serdaigle": "#4a86e8", "poufsouffle": "#e0aa1e" }

    function choisir(m) {
        if (m === "gryffondor") sGry++;
        else if (m === "serpentard") sSer++;
        else if (m === "serdaigle") sRav++;
        else sPou++;
        if (etape < questions.length - 1) etape++;
        else terminer();
    }
    function terminer() {
        var max = Math.max(sGry, sSer, sRav, sPou);
        var cand = [];
        if (sGry === max) cand.push("gryffondor");
        if (sSer === max) cand.push("serpentard");
        if (sRav === max) cand.push("serdaigle");
        if (sPou === max) cand.push("poufsouffle");
        elue = cand[Math.floor(Math.random() * cand.length)];
        etape = questions.length;
        revele.start();
    }

    Timer { id: revele; interval: 3200; onTriggered: { console.log("LUMOS_MAISON=" + win.elue); Qt.quit(); } }

    // Fond : ciel de nuit
    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#0b0720" }
            GradientStop { position: 0.55; color: "#120a28" }
            GradientStop { position: 1.0; color: "#070410" }
        }
    }
    Repeater {
        model: 90
        delegate: Rectangle {
            property real px: Math.random()
            property real py: Math.random()
            width: 1 + Math.random() * 2; height: width; radius: width
            color: "#ffffff"
            opacity: 0.2 + Math.random() * 0.6
            x: px * win.width; y: py * win.height * 0.9
        }
    }
    Rectangle {   // halo doré derrière le chapeau
        anchors.horizontalCenter: parent.horizontalCenter
        y: win.height * 0.10
        width: 360; height: 360; radius: 180
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#33d3a625" }
            GradientStop { position: 1.0; color: "#00000000" }
        }
    }

    // Le chapeau
    Canvas {
        id: chapeau
        width: 220; height: 210
        anchors.horizontalCenter: parent.horizontalCenter
        y: win.height * 0.11
        onPaint: {
            var ctx = getContext("2d");
            ctx.reset();
            // brim
            ctx.fillStyle = "#1b1430";
            ctx.beginPath();
            ctx.ellipse(20, 165, 180, 34);
            ctx.fill();
            ctx.strokeStyle = "#d3a625"; ctx.lineWidth = 2; ctx.stroke();
            // cône avachi
            ctx.fillStyle = "#241a3a";
            ctx.beginPath();
            ctx.moveTo(72, 178);
            ctx.bezierCurveTo(74, 120, 96, 70, 150, 20);
            ctx.bezierCurveTo(134, 78, 138, 120, 150, 168);
            ctx.bezierCurveTo(124, 176, 98, 180, 72, 178);
            ctx.closePath();
            ctx.fill();
            ctx.strokeStyle = "#3a2a5a"; ctx.lineWidth = 2; ctx.stroke();
            // bande + boucle dorée
            ctx.fillStyle = "#1b1430";
            ctx.beginPath(); ctx.moveTo(76, 168); ctx.bezierCurveTo(104, 178, 132, 176, 150, 166);
            ctx.lineTo(150, 150); ctx.bezierCurveTo(132, 160, 104, 162, 78, 152); ctx.closePath(); ctx.fill();
            ctx.strokeStyle = "#d3a625"; ctx.lineWidth = 2.5; ctx.stroke();
            // plis « visage »
            ctx.strokeStyle = "#0e0a1c"; ctx.lineWidth = 3; ctx.lineCap = "round";
            ctx.beginPath(); ctx.moveTo(100, 120); ctx.quadraticCurveTo(112, 128, 100, 138); ctx.stroke();
            ctx.beginPath(); ctx.moveTo(126, 120); ctx.quadraticCurveTo(138, 128, 126, 138); ctx.stroke();
            ctx.beginPath(); ctx.moveTo(104, 152); ctx.quadraticCurveTo(116, 160, 130, 150); ctx.stroke();
        }
    }

    // --- Questions ---
    Column {
        anchors.horizontalCenter: parent.horizontalCenter
        y: win.height * 0.42
        width: Math.min(820, win.width * 0.8)
        spacing: 26
        visible: win.etape < win.questions.length
        opacity: visible ? 1 : 0
        Behavior on opacity { NumberAnimation { duration: 400 } }

        Text {
            width: parent.width
            horizontalAlignment: Text.AlignHCenter
            text: win.etape < win.questions.length ? win.questions[win.etape].q : ""
            color: "#f1e6d6"; font.family: win.serif; font.pixelSize: 34; wrapMode: Text.WordWrap
        }

        Repeater {
            model: win.etape < win.questions.length ? win.questions[win.etape].opts : []
            delegate: Rectangle {
                width: parent.width; height: 64; radius: 10
                color: souris.containsMouse ? "#2a2046" : "#181030"
                border.color: souris.containsMouse ? win.or : "#3a2e5a"
                border.width: souris.containsMouse ? 2 : 1
                Behavior on color { ColorAnimation { duration: 150 } }
                Text {
                    anchors.fill: parent; anchors.leftMargin: 22; anchors.rightMargin: 22
                    verticalAlignment: Text.AlignVCenter
                    text: modelData.t; color: "#e7dcc9"
                    font.family: win.serif; font.pixelSize: 20; wrapMode: Text.WordWrap
                }
                MouseArea {
                    id: souris; anchors.fill: parent; hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: win.choisir(modelData.m)
                }
            }
        }

        Row {
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 12; topPadding: 10
            Repeater {
                model: win.questions.length
                delegate: Rectangle {
                    width: 10; height: 10; radius: 5
                    color: index <= win.etape ? win.or : "#3a2e5a"
                }
            }
        }
    }

    // --- Révélation ---
    Column {
        anchors.centerIn: parent
        anchors.verticalCenterOffset: win.height * 0.08
        spacing: 18
        visible: win.etape === win.questions.length
        opacity: visible ? 1 : 0
        Behavior on opacity { NumberAnimation { duration: 700 } }

        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: "Difficile… très difficile. Mais je sais :"
            color: "#c9bda8"; font.family: win.serif; font.italic: true; font.pixelSize: 26
        }
        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: win.elue ? win.libelles[win.elue].toUpperCase() : ""
            color: win.elue ? win.couleurs[win.elue] : win.or
            font.family: win.serif; font.pixelSize: 86; font.bold: true
            style: Text.Outline; styleColor: "#000000"
        }
    }

    Text {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom; anchors.bottomMargin: 28
        text: "Échap pour annuler"
        color: "#6a5f80"; font.family: win.serif; font.pixelSize: 15
    }

    Item {
        anchors.fill: parent; focus: true
        Keys.onEscapePressed: Qt.quit()
    }
}
