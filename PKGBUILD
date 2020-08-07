pkgname=qtile-brightnesscontrol-git
_pkgname=qtile-brightnesscontrol
pkgver=0.0.1
pkgrel=1
provides=("$_pkgname")
conflicts=("$_pkgname")
pkgdesc="Qtile code to control and display screen brightness."
url="https://github.com/elparaguayo/qtile-brightnesscontrol.git"
arch=("any")
license=("MIT")
depends=("python" "qtile")
source=("git+https://github.com/elparaguayo/$_pkgname.git")
md5sums=("SKIP")

pkgver()
{
  cd "$_pkgname"
  printf "r%s.%s" "$(git rev-list --count HEAD)" "$(git rev-parse --short HEAD)"
}

package()
{
  cd "$_pkgname"
  python setup.py install --root="$pkgdir"
  install -Dm 644 10-brightnesscontrol-backlight.rules "${pkgdir}/usr/lib/udev/rules.d/10-brightnesscontrol-backlight.rules"
}
