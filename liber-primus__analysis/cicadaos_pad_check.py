"""The 2013 CicadaOS disc (2013/02/3301.iso) holds /DATA/_560.00, 560.17 and 560.13: one-time pads ("datasets").
In 2013, callers to the poster phone numbers got e.g. "Dataset:13 Offset:12821 Data:28C07E...". XORing that data
with 560.13 at that byte offset gives an onion address. This reproduces the Portland, OR poster's result.
Needs the ISO (git lfs pull --include 2013/02/3301.iso) and pycdlib."""
import io, os, pycdlib
HERE = os.path.dirname(os.path.abspath(__file__))
iso = pycdlib.PyCdlib(); iso.open(os.path.join(HERE, '..', '2013', '02', '3301.iso'))
buf = io.BytesIO(); iso.get_file_from_iso_fp(buf, iso_path='/DATA/560.13;1'); pad = buf.getvalue()
data = bytes.fromhex('28C07E1B102D4D5C4C1A376E064477E1416FCC94928765'); off = 12821
print(bytes(a ^ b for a, b in zip(data, pad[off:off + len(data)])))
