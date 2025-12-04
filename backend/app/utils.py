from diff_match_patch import diff_match_patch

def compute_diff(text1: str, text2: str):
    """計算兩個文字之間的差異"""
    dmp = diff_match_patch()
    diffs = dmp.diff_main(text1, text2)
    dmp.diff_cleanupSemantic(diffs)
    return diffs
