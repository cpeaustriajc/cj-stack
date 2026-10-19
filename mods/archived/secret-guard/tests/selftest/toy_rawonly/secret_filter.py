import sys

for line in sys.stdin:
    sys.stdout.write(line.replace("FAKESECRET_toy1", "[REDACTED]").replace("FAKESECRET_toy2", "[REDACTED]").replace("FAKESECRET_toy3", "[REDACTED]"))
    sys.stdout.flush()
