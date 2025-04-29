from ue_tokenizer import parse, execute
import logging

logging.basicConfig(level=logging.DEBUG)

tokens = parse("Regex(\\+\\+Fortnite\\+Release-(\\d+)\\.(\\d+).*-CL-(\\d+)-.*) && ((RegexGroupInt64(1) > 34 || (RegexGroupInt64(1) == 34 && RegexGroupInt64(2) >= 10)) && RegexGroupInt64(3) >= 39555844)")

cases = ["++Fortnite+Release-34.40-CL-41753727-Windows", "unsupported text"]


logger = logging.getLogger()
for case in cases:
    logger.info(f"Result of \"{case}\" -> {execute(tokens, case)}")
