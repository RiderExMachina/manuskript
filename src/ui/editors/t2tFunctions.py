#!/usr/bin/env python
# -*- coding: utf-8 -*-

from qt import *


def textToFormatArray(text):
    """
    Take some text and returns an array of array containing informations
    about how the text is formatted:
    r = [ [0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0],
          [0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1],
          ...
        ]
    Each sub-array is for one of the beautifier:
        0: bold
        1: italic
        2: underline
        3: strike
        4: code
        5: tagged

    Each sub-array contains an element for each character of the text, with the
    value 1 if it is formatted in the specific format, -1 if it is markup, and
    0 otherwise.

    removeMarks returns a both the array and a string, in which all of the
    formatting marks have been removed.
    """

    result = []

    for markup in ["\*", "/", "_", "-", "`", "\'"]:

        rList = []

        r = QRegExp(r'(' + markup * 2 + ')(.+)(' + markup * 2 + ')')
        r.setMinimal(True)
        pos = r.indexIn(text, 0)
        lastPos = 0
        while pos >= 0:
            #We have a winner
            rList += [0] * (pos - lastPos)
            rList += [2] * 2
            rList += [1] * len(r.cap(2))
            rList += [2] * 2
            lastPos = pos + len(r.cap(0))
            pos = r.indexIn(text, len(rList))

        if len(rList) < len(text):
            rList += [0] * (len(text) - len(rList))

        result.append(rList)

    return result


def textToFormatArrayNoMarkup(text):
    """
    Same as textToFormatArray, except that it removes all the markup from the
    text and returns two elements:
        the array
        the text without markup
    """

    r = textToFormatArray(text)
    result = [[], [], [], [], [], []]
    rText = ""

    for i in range(len(text)):
        t = max([k[i] for k in r])  # kind of flattens all the format array
        if t != 2:
            rText += text[i]
            [result[k].append(r[k][i]) for k in range(len(r))]

    return rText, result


def translateSelectionToUnformattedText(text, start, end):
    """
    Translate the start / end of selection from a formatted text to an
    unformatted one.
    """
    r = textToFormatArray(text)

    rStart, rEnd = start, end

    for i in range(len(text)):
        t = max([k[i] for k in r])  # kind of flattens all the format array
        if t == 2:  # t == 2 means this character is markup
            if i <= start: rStart -= 1
            if i < end: rEnd -= 1

    return rStart, rEnd


def translateSelectionToFormattedText(text, start, end):
    """
    Translate the start / end of selection from a formatted text to an
    unformatted one.
    """
    r = textToFormatArray(text)

    rStart, rEnd = start, end

    for i in range(len(text)):
        t = max([k[i] for k in r])  # kind of flattens all the format array
        if t == 2:  # t == 2 means this character is markup
            if i <= start: rStart -= 1
            if i < end: rEnd -= 1

    return rStart, rEnd


def printArray(array):
    print(("".join([str(j) for j in array])))


def printArrays(arrays):
    for i in arrays: printArray(i)


def reformatText(text, markupArray):
    """
    Takes a text without formatting markup, and an array generated by
    textToFormatArray, and adds the propper markup.
    """

    rText = ""
    markup = ["**", "//", "__", "--", "``", "''"]

    for k in range(len(markupArray)):
        m = markupArray[k]
        open = False  # Are we in an openned markup
        d = 0
        alreadySeen = []
        for i in range(len(text)):
            insert = False
            if not open and m[i] == 1:
                insert = True
                open = True

            if open and m[i] == 0:
                insert = True
                open = False
            if open and m[i] > 1:
                z = i
                while m[z] == m[i]: z += 1
                if m[z] != 1 and not m[i] in alreadySeen:
                    insert = True
                    open = False
                alreadySeen.append(m[i])
            if insert:
                rText += markup[k]
                for j in range(len(markupArray)):
                    # The other array still have the same length
                    if j > k:
                        #Insert 2 for bold, 3 for italic, etc.
                        markupArray[j].insert(i + d, k + 2)
                        markupArray[j].insert(i + d, k + 2)
                    alreadySeen = []
                d += 2
            rText += text[i]
        if open:
            rText += markup[k]
            for j in range(len(markupArray)):
                # The other array still have the same length
                if j > k:
                    #Insert 2 for bold, 3 for italic, etc.
                    markupArray[j].insert(i + d, k + 2)
                    markupArray[j].insert(i + d, k + 2)
        text = rText
        rText = ""

    ## Clean up
    # Exclude first and last space of the markup
    for markup in ["\*", "/", "_", "-", "`", "\'"]:
        r = QRegExp(r'(' + markup * 2 + ')(\s+)(.+)(' + markup * 2 + ')')
        r.setMinimal(True)
        text.replace(r, "\\2\\1\\3\\4")
        r = QRegExp(r'(' + markup * 2 + ')(.+)(\s+)(' + markup * 2 + ')')
        r.setMinimal(True)
        text.replace(r, "\\1\\2\\4\\3")

    return text


def cleanFormat(text):
    "Makes markup clean (removes doubles, etc.)"
    t, a = textToFormatArrayNoMarkup(text)
    return reformatText(t, a)


class State:
    NORMAL = 0
    TITLE_1 = 1
    TITLE_2 = 2
    TITLE_3 = 3
    TITLE_4 = 4
    TITLE_5 = 5
    NUMBERED_TITLE_1 = 6
    NUMBERED_TITLE_2 = 7
    NUMBERED_TITLE_3 = 8
    NUMBERED_TITLE_4 = 9
    NUMBERED_TITLE_5 = 10
    TITLES = [TITLE_1, TITLE_2, TITLE_3, TITLE_4, TITLE_5, NUMBERED_TITLE_1,
              NUMBERED_TITLE_2, NUMBERED_TITLE_3, NUMBERED_TITLE_4,
              NUMBERED_TITLE_5]
    # AREA
    COMMENT_AREA = 11
    CODE_AREA = 12
    RAW_AREA = 13
    TAGGED_AREA = 14
    # AREA MARKUP
    COMMENT_AREA_BEGINS = 15
    COMMENT_AREA_ENDS = 16
    CODE_AREA_BEGINS = 17
    CODE_AREA_ENDS = 18
    RAW_AREA_BEGINS = 19
    RAW_AREA_ENDS = 20
    TAGGED_AREA_BEGINS = 21
    TAGGED_AREA_ENDS = 22
    #LINE
    COMMENT_LINE = 30
    CODE_LINE = 31
    RAW_LINE = 32
    TAGGED_LINE = 33
    SETTINGS_LINE = 34
    BLOCKQUOTE_LINE = 35
    HORIZONTAL_LINE = 36
    HEADER_LINE = 37
    # LIST
    LIST_BEGINS = 40
    LIST_ENDS = 41
    LIST_EMPTY = 42
    LIST_BULLET = 43
    LIST_BULLET_ENDS = 44
    LIST = [40, 41, 42] + list(range(100, 201))
    # TABLE
    TABLE_LINE = 50
    TABLE_HEADER = 51
    #OTHER
    MARKUP = 60
    LINKS = 61
    MACRO = 62
    DEFAULT = 63

    @staticmethod
    def titleLevel(state):
        """
        Returns the level of the title, from the block state.
        """
        return {
            State.TITLE_1: 1,
            State.TITLE_2: 2,
            State.TITLE_3: 3,
            State.TITLE_4: 4,
            State.TITLE_5: 5,
            State.NUMBERED_TITLE_1: 1,
            State.NUMBERED_TITLE_2: 2,
            State.NUMBERED_TITLE_3: 3,
            State.NUMBERED_TITLE_4: 4,
            State.NUMBERED_TITLE_5: 5,
        }.get(state, -1)