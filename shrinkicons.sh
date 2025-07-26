for f in content/*/icon.jpg; do
    # 32x32 pixel icon
    convert "$f" -resize 32x32\! "$f-32x32.jpg"
    # 64x64 pixel icon
    convert "$f" -resize 64x64\! "$f-64x64.jpg"
done