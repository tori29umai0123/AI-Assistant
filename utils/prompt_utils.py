def filterTag(execute_tags, prompt_list):
    return [t for t in prompt_list if t not in execute_tags]

def remove_duplicates(tags):
    # タグの重複を取り除く
    seen = set()
    unique_tags = []
    for tag in tags:
        tag_clean = tag.lower().strip()
        if tag_clean not in seen and tag_clean != "":
            unique_tags.append(tag)
            seen.add(tag_clean)
    return unique_tags


def remove_color(tags):
    # タグの色情報を取り除く
    color_list = ["pink", "red", "orange", "brown", "yellow", "green", "blue", "purple", "blonde"]
    # カラータグを除去します。
    cleaned_tags = [tag for tag in tags if not any(color.lower() in tag.lower() for color in color_list)]
    return cleaned_tags


def prepare_prompt(execute_tags, base_prompt):
    prompt_list = base_prompt.split(", ")
    # execute_tagsを除去
    filtered_tags = filterTag(execute_tags, prompt_list)
    # カラータグを除去
    removed_color_tags = remove_color(filtered_tags)
    # 除去されたカラータグから重複を除去
    unique_tags = remove_duplicates(removed_color_tags)
    # 最終的なプロンプトを生成
    return ", ".join(unique_tags)