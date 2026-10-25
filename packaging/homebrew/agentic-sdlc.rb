# Homebrew formula for agentic-sdlc.
#
# This lives here rather than in a tap so the formula is versioned with the code it installs.
# To publish it, copy this file into a tap repository (for example mdferdousalam/homebrew-tap,
# as Formula/agentic-sdlc.rb) and users then run:
#
#   brew install mdferdousalam/tap/agentic-sdlc
#
# On each release: bump url and version, recompute sha256 with
#   curl -fsSL <url> | shasum -a 256
class AgenticSdlc < Formula
  desc "Enforced agent-based SDLC pipeline for any coding agent"
  homepage "https://github.com/mdferdousalam/agentic-sdlc"
  url "https://github.com/mdferdousalam/agentic-sdlc/archive/refs/tags/v2.3.0.tar.gz"
  version "2.3.0"
  sha256 "ef1cdc5b1fd515c27dd27745b9653eaac4cdf5cca80eb6d2afa6f6366ce24b17"
  license "MIT"

  depends_on "python@3.12"
  depends_on "git"

  def install
    # The CLI reads agents/, commands/, docs/ and profiles/ relative to its own parent, so the
    # tree ships whole into libexec and only the entry point is linked onto PATH.
    libexec.install Dir["*"]
    (libexec/"bin/sdlc").chmod 0755
    (bin/"sdlc").write <<~SH
      #!/bin/sh
      exec "#{Formula["python@3.12"].opt_bin}/python3.12" "#{libexec}/bin/sdlc" "\"
    SH
    (bin/"sdlc").chmod 0755
  end

  def caveats
    <<~EOS
      Next, inside a repository you work in:
        sdlc install     # detect your coding agents and set each one up
        sdlc doctor      # what is configured, and what is missing

      What each agent can actually enforce:
        #{libexec}/docs/platforms.md
    EOS
  end

  test do
    system bin/"sdlc", "--help"
    assert_match "agentic-sdlc", shell_output("#{bin}/sdlc install --list")
  end
end
