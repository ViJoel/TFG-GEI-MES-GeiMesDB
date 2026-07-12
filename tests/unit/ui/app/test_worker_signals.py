from ui.app.worker_signals import WorkerSignals


def test_worker_signals(qtbot):
    """
    Verifica que las señales del Worker se emiten.
    """

    signals = WorkerSignals()

    with qtbot.waitSignal(signals.success):
        signals.success.emit("ok")

    with qtbot.waitSignal(signals.error):
        signals.error.emit(Exception())

    with qtbot.waitSignal(signals.finished):
        signals.finished.emit()
