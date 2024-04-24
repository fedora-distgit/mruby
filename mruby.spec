%define soversion %(echo '%{version}' | cut -f 1-2 -d '.')

Name:           mruby
Version:        3.3.0
Release:        1.1%{?dist}
Summary:        Lightweight implementation of the Ruby language
License:        MIT
URL:            https://github.com/mruby/mruby

Source0:        https://github.com/mruby/mruby/archive/refs/tags/%{version}.tar.gz#/%{name}-%{version}.tar.gz

BuildRequires:  gcc
BuildRequires:  gcc-c++
# >>> Direct file require might be better
BuildRequires:  %{_bindir}/rake
BuildRequires:  doxygen
BuildRequires:  graphviz

%description
Mruby is the lightweight implementation of the Ruby language complying to
(part of) the ISO standard with more recent features provided by Ruby 3.x.
Also, its syntax is Ruby 3.x compatible except for pattern matching.

%package devel
Summary: Development libraries and header files for %{name}
%description devel
%{summary}.

%package static
Summary: Static library of %{name}
%description static
%{summary}.

%package doc
Summary: Documentation for %{name}
Requires:  js-jquery
%description doc
%{summary}.

%prep
%setup -q

%build
# >>> I have no insight into the flags; I hope someone will verify
CFLAGS+='-fpic'
LDFLAGS+='-lm'

rake -v all

pushd build/host
rm bin/*
gcc -shared -o lib/libmruby.so.%{soversion} ${LDFLAGS} -Wl,-soname,libmruby.so.%{soversion} -Wl,--whole-archive lib/libmruby.a -Wl,--no-whole-archive
gcc ${CFLAGS} -o "bin/mrbc" mrbgems/mruby-bin-mrbc/tools/mrbc/*.o ${LDFLAGS} "lib/libmruby_core.a"

# >>> Maybe let's simplify this?
for _binary in m{irb,rdb,ruby,ruby-strip}; do
gcc ${CFLAGS} -o "bin/${_binary}"  mrbgems/mruby-bin-*/tools/${_binary}/*.o ${LDFLAGS} -L"lib" -Wl,-Bdynamic -lmruby
done
popd

rake -v doc:capi

%install
export PREFIX=%{buildroot}%{_prefix}
rake install
mv %{buildroot}%{_prefix}/lib %{buildroot}%{_libdir}
ln -s libmruby.so.%{soversion} %{buildroot}%{_libdir}/libmruby.so

mkdir -p %{buildroot}%{_docdir}/%{name}
rm doc/capi/html/jquery.js
ln -s %{_datadir}/javascript/jquery/latest/jquery.js doc/capi/html/jquery.js
mv -t %{buildroot}%{_docdir}/%{name} doc/capi/html

%check
export LD_LIBRARY_PATH='%{buildroot}%{_libdir}'
rake test

%files
%license LICENSE
%doc README.md
%{_bindir}/mirb
%{_bindir}/mrbc
%{_bindir}/mrdb
%{_bindir}/mruby
%{_libdir}/libmruby.so.%{soversion}

%files devel
%{_libdir}/libmruby.so
%{_includedir}/*

%files static
%license LICENSE
%{_bindir}/mruby-config
%{_bindir}/mruby-strip
%{_libdir}/libmruby.a
%{_libdir}/libmruby_core.a
%{_libdir}/libmruby.flags.mak

%files doc
%license LICENSE
%{_docdir}/%{name}/html

%changelog
* Mon Apr 15 2024 Marian Koncek <mkoncek@redhat.com> - 3.3.0-1
- Initial build
