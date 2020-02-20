# -*- coding: utf-8 -*-
# !/usr/bin/env python
import sys

from user_agents import parse as parse_ua


def main(argv=sys.argv[1:]):
    # entry_no, user_agentの順で、テキストファイルに入れること
    entry_user_agent_file = open(argv[0], "r")

    for line in entry_user_agent_file:
        data = line.split("|")
        entry_no = data[0].strip()
        user_agent = data[1].strip()

        ua = parse_ua(user_agent)

        print "{}, {}".format("PC" if ua.is_pc else "スマホ", entry_no)

    entry_user_agent_file.close()


if __name__ == '__main__':
    main()
