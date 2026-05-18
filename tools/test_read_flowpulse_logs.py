import unittest

from tools import read_flowpulse_logs as reader


def hex_word(value: int) -> str:
    return f"{value:064x}"


def bytes32(fill: str) -> str:
    return "0x" + (fill * 32)


def topic_address(address: str) -> str:
    return "0x" + ("0" * 24) + address[2:].lower()


def abi_string_tail(value: str) -> str:
    raw = value.encode("utf-8").hex()
    padded_len = ((len(raw) + 63) // 64) * 64
    return hex_word(len(value.encode("utf-8"))) + raw.ljust(padded_len, "0")


class FlowPulseReaderTest(unittest.TestCase):
    def test_decodes_flowpulse_event(self):
        uri = "flowmemory://uniswap-v4/after-swap"
        data = (
            "0x"
            + hex_word(4)
            + ("33" * 32)
            + ("44" * 32)
            + ("55" * 32)
            + hex_word(7)
            + hex_word(123)
            + hex_word(7 * 32)
            + abi_string_tail(uri)
        )

        decoded = reader.decode_flowpulse(
            {
                "topics": [
                    reader.FLOWPULSE_TOPIC,
                    bytes32("11"),
                    bytes32("22"),
                    topic_address("0x1234567890123456789012345678901234567890"),
                ],
                "data": data,
            }
        )

        self.assertEqual(decoded["eventName"], "FlowPulse")
        self.assertEqual(decoded["pulseType"], "SWAP_MEMORY_SIGNAL")
        self.assertEqual(decoded["pulseId"], bytes32("11"))
        self.assertEqual(decoded["rootfieldId"], bytes32("22"))
        self.assertEqual(decoded["actor"], "0x1234567890123456789012345678901234567890")
        self.assertEqual(decoded["subjectPoolId"], bytes32("33"))
        self.assertEqual(decoded["commitment"], bytes32("44"))
        self.assertEqual(decoded["parentPulseId"], bytes32("55"))
        self.assertEqual(decoded["sequence"], "7")
        self.assertEqual(decoded["occurredAt"], "123")
        self.assertEqual(decoded["uri"], uri)
        self.assertEqual(decoded["validation"], [])

    def test_decodes_after_swap_observed_event(self):
        decoded = reader.decode_after_swap_observed(
            {
                "topics": [
                    reader.AFTER_SWAP_OBSERVED_TOPIC,
                    topic_address("0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"),
                    topic_address("0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"),
                    bytes32("cc"),
                ],
                "data": "0x" + ("dd" * 32) + ("ee" * 32) + ("ff" * 32),
            }
        )

        self.assertEqual(decoded["eventName"], "AfterSwapObserved")
        self.assertEqual(decoded["caller"], "0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        self.assertEqual(decoded["sender"], "0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb")
        self.assertEqual(decoded["poolId"], bytes32("cc"))
        self.assertEqual(decoded["rootfieldId"], bytes32("dd"))
        self.assertEqual(decoded["commitment"], bytes32("ee"))
        self.assertEqual(decoded["hookDataHash"], bytes32("ff"))

    def test_marks_zero_rootfield_and_commitment(self):
        data = (
            "0x"
            + hex_word(4)
            + ("33" * 32)
            + ("00" * 32)
            + ("00" * 32)
            + hex_word(1)
            + hex_word(123)
            + hex_word(7 * 32)
            + abi_string_tail("")
        )

        decoded = reader.decode_flowpulse(
            {
                "topics": [
                    reader.FLOWPULSE_TOPIC,
                    bytes32("11"),
                    reader.ZERO32,
                    topic_address("0x1234567890123456789012345678901234567890"),
                ],
                "data": data,
            }
        )

        self.assertIn("zero_rootfield", decoded["validation"])
        self.assertIn("zero_commitment", decoded["validation"])


if __name__ == "__main__":
    unittest.main()
