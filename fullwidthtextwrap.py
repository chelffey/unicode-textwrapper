"""
subclass on python textwrap class that implements east asian width wrapping.
Written in April 2022. Based on the most updated TextWrapper python library 
class at that point in time. 
"""

from textwrap import TextWrapper
import unicodedata

class EAWTextWrapper(TextWrapper):

    # unicon character widths
    # full-width characters have a length of 2
    #     half-width characters have a length of 1
    #     reference for unicode East Asian width property:
    #     https://en.wikipedia.org/wiki/Halfwidth_and_fullwidth_forms 
    char_widths = {
        'W' : 2, # naturally wide, e.g. Hiragana
        'Na' : 1, # naturally narrow, e.g. Basic Latin alphabet
        'F' : 2, # wide variant
        'H' : 1, # halfwidth variant, e.g. narrow Katakana
        'A' : 2, # ambiguous, width varies
        'N' : 1 # neutral
    }

    def _eaw_str_len(self, word):
        """
        length of unicode string considering east asian width of each character
        """
        return sum(self.char_widths[unicodedata.east_asian_width(char)] for char in word)
    
    def _eaw_space_left(self, word, space_left):
        """
        return the index at which all the space_left is filled, 
        considering east asian width of each character.
        word = input string
        space_left = width, as measured by number of narrow characters

        """
        cur_length = 0
        index = 0
        for char in word:
            cur_length += self.char_widths[unicodedata.east_asian_width(char)]
            if (cur_length > space_left):
                return index
            index += 1
        return index

    def _wrap_chunks(self, chunks):
        """ This function is from lib/textwrap.py
        The only change is to use the self._eaw_str_len() function. 
        ---
        _wrap_chunks(chunks : [string]) -> [string]

        Wrap a sequence of text chunks and return a list of lines of
        length 'self.width' or less.  (If 'break_long_words' is false,
        some lines may be longer than this.)  Chunks correspond roughly
        to words and the whitespace between them: each chunk is
        indivisible (modulo 'break_long_words'), but a line break can
        come between any two chunks.  Chunks should not have internal
        whitespace; ie. a chunk is either all whitespace or a "word".
        Whitespace chunks will be removed from the beginning and end of
        lines, but apart from that whitespace is preserved.
        """

        lines = []
        if self.width <= 0:
            raise ValueError("invalid width %r (must be > 0)" % self.width)
        if self.max_lines is not None:
            if self.max_lines > 1:
                indent = self.subsequent_indent
            else:
                indent = self.initial_indent
            if len(indent) + len(self.placeholder.lstrip()) > self.width:
                raise ValueError("placeholder too large for max width")

        # Arrange in reverse order so items can be efficiently popped
        # from a stack of chucks.
        chunks.reverse()

        while chunks:

            # Start the list of chunks that will make up the current line.
            # cur_len is just the length of all the chunks in cur_line.
            cur_line = []
            cur_len = 0

            # Figure out which static string will prefix this line.
            if lines:
                indent = self.subsequent_indent
            else:
                indent = self.initial_indent

            # Maximum width for this line.
            width = self.width - len(indent)

            # First chunk on line is whitespace -- drop it, unless this
            # is the very beginning of the text (ie. no lines started yet).
            if self.drop_whitespace and chunks[-1].strip() == '' and lines:
                del chunks[-1]

            while chunks:
                l = self._eaw_str_len(chunks[-1])

                # Can at least squeeze this chunk onto the current line.
                if cur_len + l <= width:
                    cur_line.append(chunks.pop())
                    cur_len += l

                # Nope, this line is full.
                else:
                    break

            # The current line is full, and the next chunk is too big to
            # fit on *any* line (not just this one).
            if chunks and self._eaw_str_len(chunks[-1]) > width:
                self._handle_long_word(chunks, cur_line, cur_len, width)
                cur_len = sum(map(self._eaw_str_len, cur_line))

            # If the last chunk on this line is all whitespace, drop it.
            if self.drop_whitespace and cur_line and cur_line[-1].strip() == '':
                cur_len -= len(cur_line[-1])
                del cur_line[-1]

            if cur_line:
                if (self.max_lines is None or
                    len(lines) + 1 < self.max_lines or
                    (not chunks or
                     self.drop_whitespace and
                     len(chunks) == 1 and
                     not chunks[0].strip()) and cur_len <= width):
                    # Convert current line back to a string and store it in
                    # list of all lines (return value).
                    lines.append(indent + ''.join(cur_line))
                else:
                    while cur_line:
                        if (cur_line[-1].strip() and
                            cur_len + len(self.placeholder) <= width):
                            cur_line.append(self.placeholder)
                            lines.append(indent + ''.join(cur_line))
                            break
                        cur_len -= len(cur_line[-1])
                        del cur_line[-1]
                    else:
                        if lines:
                            prev_line = lines[-1].rstrip()
                            if (len(prev_line) + len(self.placeholder) <=
                                    self.width):
                                lines[-1] = prev_line + self.placeholder
                                break
                        lines.append(indent + self.placeholder.lstrip())
                    break

        return lines


    def _handle_long_word(self, reversed_chunks, cur_line, cur_len, width):
        """This function is from lib/textwrap.py
        The only change is to use the self._eaw_str_len() function and 
        the self._eaw_space_left() function.
        ---
        _handle_long_word(chunks : [string],
                             cur_line : [string],
                             cur_len : int, width : int)

        Handle a chunk of text (most likely a word, not whitespace) that
        is too long to fit in any line.
        """
        # Figure out when indent is larger than the specified width, and make
        # sure at least one character is stripped off on every pass
        if width < 1:
            space_left = 1
        else:
            space_left = width - cur_len

        # If we're allowed to break long words, then do so: put as much
        # of the next chunk onto the current line as will fit.
        if self.break_long_words:
            # end = space_left # TODO its assuming 1 char = 1 space. 
            chunk = reversed_chunks[-1]
            end = self._eaw_space_left(chunk, space_left)
            if self.break_on_hyphens and self._eaw_str_len(chunk) > space_left:
                # break after last hyphen, but only if there are
                # non-hyphens before it
                hyphen = chunk.rfind('-', 0, space_left)
                if hyphen > 0 and any(c != '-' for c in chunk[:hyphen]):
                    end = hyphen + 1
            cur_line.append(chunk[:end])  
            reversed_chunks[-1] = chunk[end:]

        # Otherwise, we have to preserve the long word intact.  Only add
        # it to the current line if there's nothing already there --
        # that minimizes how much we violate the width constraint.
        elif not cur_line:
            cur_line.append(reversed_chunks.pop())

        # If we're not allowed to break long words, and there's already
        # text on the current line, do nothing.  Next time through the
        # main loop of _wrap_chunks(), we'll wind up here again, but
        # cur_len will be zero, so the next line will be entirely
        # devoted to the long word that we can't handle right now.