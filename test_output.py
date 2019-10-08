"""
    DO NOT MODIFY

    A script to test whether the contents of output.txt match the expected value
    produced by a valid solution
"""

with open('./output.txt', 'r') as file:
    contents = file.read()

    # get lines with text, last line extra last line because of match on last character
    lines = [line for line in contents.split('\n\n') if len(line) != 0]
    
    for line in lines:
        assert line.strip() == 'Maestro is the best......', \
            f'expecting "Maestro is the best......" per line, got "{ line }"'

    assert len(lines) == 25, \
        f'expecting 25 lines, got { len(lines) }'
