for package_path in packages/*; do
    package_name=${package_path%/}
    npx nx lint $package_name
done