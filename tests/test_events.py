"""tests.test_events: Ensure that the event system can correctly register and emit events."""

import unittest
from unittest.mock import Mock

from core.events import Signal, ViewEvents


class TestSignal(unittest.IsolatedAsyncioTestCase):
    """Test the Signal class for correct registration and emission of events."""

    async def test_signal_registration_and_emission(self):
        """Test that functions can be registered to a signal and that emitting
        the signal calls those functions with the correct data."""

        # ARRANGE: Create a signal and a mock function to connect to it
        signal = Signal()
        mock_function = Mock()

        # ACT: Connect the mock function to the signal and emit an event
        signal.connect(mock_function)
        event_data = "test event"
        await signal.emit(event_data)

        # ASSERT: Verify that the mock function was called with the correct data
        mock_function.assert_called_once_with(event_data)

    async def test_signal_registration_and_emission_multiple_functions(self):
        """Test that multiple functions can be registered to a signal and that
        emitting the signal calls all registered functions with the correct data."""

        # ARRANGE: Create a signal and multiple mock functions to connect to it
        signal = Signal()
        mock_function1 = Mock()
        mock_function2 = Mock()

        # ACT: Connect the mock functions to the signal and emit an event
        signal.connect(mock_function1)
        signal.connect(mock_function2)
        event_data = "test event"
        await signal.emit(event_data)

        # ASSERT: Verify that both mock functions were called with the correct data
        mock_function1.assert_called_once_with(event_data)
        mock_function2.assert_called_once_with(event_data)

    async def test_signal_missing_functions(self):
        """Test that emitting a signal with no registered functions does not
        raise an error."""

        # ARRANGE: Create a signal with no registered functions
        signal = Signal()

        # ACT & ASSERT: Emit the signal and verify that no error is raised
        try:
            await signal.emit("test event")
        except Exception as e:
            self.fail(
                f"Emitting a signal with no registered functions raised an exception: {e}"
            )

    async def test_signal_registration_of_non_callable(self):
        """Test that connecting a non-callable object to a signal raises an error."""

        # ARRANGE: Create a signal and a non-callable object
        signal = Signal()
        non_callable = "I am not a function"

        # ACT & ASSERT: Attempt to connect the non-callable object and verify that an error is raised
        with self.assertRaises(TypeError):
            signal.connect(non_callable)  # type: ignore (this is intentional to test error handling)


class TestViewEvents(unittest.IsolatedAsyncioTestCase):
    """Test the ViewEvents class to ensure it initializes the expected signals."""

    async def test_view_events_initialization(self):
        """Test that the ViewEvents class initializes the on_user_input signal."""

        # ARRANGE & ACT: Create an instance of ViewEvents
        view_events = ViewEvents()

        # ASSERT: Verify that the on_user_input signal is initialized and is an instance of Signal
        self.assertIsInstance(view_events.on_user_input, Signal)

    async def test_view_events_on_user_input_signal(self):
        """Test that the on_user_input signal can register and emit events correctly."""

        # ARRANGE: Create an instance of ViewEvents and a mock function to connect to the on_user_input signal
        view_events = ViewEvents()
        mock_function = Mock()

        # ACT: Connect the mock function to the on_user_input signal and emit an event
        view_events.on_user_input.connect(mock_function)
        event_data = "user input event"
        await view_events.on_user_input.emit(event_data)

        # ASSERT: Verify that the mock function was called with the correct data
        mock_function.assert_called_once_with(event_data)


if __name__ == "__main__":
    unittest.main()
