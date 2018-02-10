class Solution(object):

    def longestCommonPrefix(self, strs):
        """
        :type strs: List[str]
        :rtype: str
        """
        if not strs:
            return ''
        for i, chars in enumerate(zip(*strs)):
            # print(i)
            # print(chars)
            if len(set(chars)) > 1:
                print(set(chars))
                return strs[0][:i]
        return min(strs)


if __name__ == '__main__':
    foo = Solution()
    print(foo.longestCommonPrefix(['abcd', 'abyjk']))
