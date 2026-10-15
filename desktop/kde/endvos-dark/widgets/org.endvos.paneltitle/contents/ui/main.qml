// SPDX-License-Identifier: MIT
import QtQuick
import QtQuick.Layouts
import QtQml.Models
import org.kde.plasma.plasmoid
import org.kde.plasma.core as PlasmaCore
import org.kde.plasma.components as PlasmaComponents
import org.kde.kirigami as Kirigami
import org.kde.taskmanager as TaskManager
import org.kde.plasma.private.mpris as Mpris
import "Title.js" as Title

PlasmoidItem {
    id: root

    property bool hasWindow: false
    property string windowTitle: ""
    readonly property var player: media.currentPlayer
    readonly property string displayTitle: Title.chooseTitle(
        hasWindow, windowTitle,
        player ? player.playbackStatus === Mpris.PlaybackStatus.Playing : false,
        player ? player.track : "", player ? player.artist : "")

    Plasmoid.status: PlasmaCore.Types.ActiveStatus
    Plasmoid.constraintHints: Plasmoid.CanFillArea
    preferredRepresentation: fullRepresentation
    Layout.fillWidth: true
    Layout.minimumWidth: Kirigami.Units.gridUnit * 2
    toolTipMainText: displayTitle
    toolTipTextFormat: Text.PlainText

    // No polling or shell processes. Task roles update on focus/title changes.
    function updateWindow() {
        for (let i = 0; i < windows.count; ++i) {
            const window = windows.objectAt(i);
            if (window && window.activeWindow) {
                windowTitle = window.caption;
                hasWindow = true;
                return;
            }
        }
        hasWindow = false;
        windowTitle = "";
    }

    TaskManager.TasksModel {
        id: tasks
        groupMode: TaskManager.TasksModel.GroupDisabled
        filterByScreen: false
    }

    Instantiator {
        id: windows
        model: tasks
        delegate: QtObject {
            required property var model
            readonly property bool activeWindow: model.IsActive
            readonly property string caption: model.display || ""
            onActiveWindowChanged: Qt.callLater(root.updateWindow)
            onCaptionChanged: Qt.callLater(root.updateWindow)
        }
        onObjectAdded: Qt.callLater(root.updateWindow)
        onObjectRemoved: Qt.callLater(root.updateWindow)
    }

    Mpris.Mpris2Model { id: media }

    fullRepresentation: PlasmaComponents.Label {
        text: root.displayTitle
        textFormat: Text.PlainText
        elide: Text.ElideRight
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        color: Kirigami.Theme.textColor
        Layout.fillWidth: true
        Layout.minimumWidth: Kirigami.Units.gridUnit * 2
        Accessible.name: text
    }
}
