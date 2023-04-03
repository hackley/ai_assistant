description = {
    "action": "test_action",
    "description": "Used to test the assistant. Responds with the same input you send.",
    "arguments": {
        "input": "A string to return.",
    }
}


def test_action(args):
  text = args.get('input')
  if text:
    return text
  else:
    return "ERROR: No input provided."
