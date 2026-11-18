;; Tests for the skill's scripts/sentence_per_line.clj, with Babashka's clojure.test.
;;
;; Most cases call the program's functions on a parsed document, which needs `cmark-gfm` on PATH.
;; The end-to-end cases run the command: `$SENTENCE_PER_LINE` when set (the packaged program, in
;; `nix flake check`), else `bb` on the script.
;; Run them with `bb test`, which puts the script on the classpath.

(ns sentence-per-line-test
  (:require [babashka.fs :as fs]
            [babashka.process :as process]
            [clojure.java.io :as io]
            [clojure.string :as str]
            [clojure.test :refer [deftest is testing use-fixtures]]
            [sentence-per-line :as spl]))

(def script
  (str (io/file (io/resource "sentence_per_line.clj"))))

(def command
  (if-let [program (not-empty (System/getenv "SENTENCE_PER_LINE"))]
    [program]
    ["bb" script]))

(def fence "```")

(defn flagged
  "The line numbers the check flags in Markdown text, from the program's own functions."
  [text]
  (let [text (spl/blank-front-matter text)]
    (spl/flagged-lines (spl/parse-markdown text) (str/split-lines text))))

;; End-to-end helpers

(def ^:dynamic *directory* nil)

(use-fixtures :each
  (fn [test]
    (let [directory (fs/create-temp-dir)]
      (try
        (binding [*directory* directory] (test))
        (finally (fs/delete-tree directory))))))

(defn write
  ([text] (write text "doc.md"))
  ([text file-name]
   (let [path (str (fs/path *directory* file-name))]
     (spit path text)
     path)))

(defn run [& args]
  (apply process/shell {:out :string :err :string :continue true} (concat command args)))

;; Pure functions

(deftest hard-break
  (is (spl/hard-break? "Label  "))
  (is (spl/hard-break? "Label\\"))
  (is (not (spl/hard-break? "Label "))))

(deftest ends-sentence
  (is (every? spl/ends-sentence? ["Done." "Done!" "Done?" "Done…" "(Done.)" "**Done.**" "`done.`"]))
  (is (not-any? spl/ends-sentence? ["Not done" "The fix:" "then;" "**bold**" ""])))

(deftest blank-front-matter
  (testing "a leading front matter block is emptied, keeping its lines"
    (is (= "\n\n\nText." (spl/blank-front-matter "---\nname: x\n---\nText."))))
  (testing "text without front matter is unchanged"
    (is (= "Text.\n\n---\n" (spl/blank-front-matter "Text.\n\n---\n")))))

(deftest report-lines
  (is (= ["a.md:3: ends mid-sentence; break lines only between sentences"]
         (spl/report-lines "a.md" [3]))))

;; Prose

(deftest one-sentence-per-line-passes
  (is (= [] (flagged "First sentence.\nSecond one!\nThird?\nFourth…\n"))))

(deftest hard-wrapped-paragraph-flags-each-line-ending-mid-sentence
  (is (= [1 2] (flagged "A sentence wrapped\nat a column, then. Another\nthat ends here.\n"))))

(deftest last-line-of-a-paragraph-is-never-flagged
  (is (= [] (flagged "No period here\n\nNor here\n"))))

(deftest closing-marks-after-the-punctuation-are-skipped
  (is (= [] (flagged "See (this one.)\n**Bold.**\n_Em._\n\"Quoted.\"\n`code.`\nEnd.\n"))))

(deftest line-ending-in-emphasis-or-a-link-without-punctuation-is-flagged
  (is (= [1 2] (flagged "Some **bold**\ntext and a [link](https://example.com)\nend.\n"))))

(deftest colon-and-semicolon-do-not-end-a-sentence
  (is (= [1 2] (flagged "The fix:\nrestart it; then\ncheck.\n"))))

(deftest line-ending-inside-a-code-span-is-flagged
  (is (= [1] (flagged "Run `nix\nfmt` first.\n"))))

;; Hard breaks

(deftest two-trailing-spaces-are-a-hard-break
  (is (= [] (flagged "**Label**  \nvalue\n"))))

(deftest trailing-backslash-is-a-hard-break
  (is (= [] (flagged "**Label**\\\nvalue\n"))))

(deftest lines-after-a-hard-break-are-still-checked
  (is (= [2] (flagged "Label\\\nvalue that\nwraps.\n"))))

;; Blocks

(deftest fenced-code-block-is-ignored
  (is (= [] (flagged (str "Intro.\n\n" fence "\ncode that\nwraps\n" fence "\n")))))

(deftest tilde-fence-inside-a-list-item-is-ignored
  (is (= [] (flagged "- Item.\n\n  ~~~\n  code that\n  wraps\n  ~~~\n"))))

(deftest indented-code-block-is-ignored
  (is (= [] (flagged "Intro.\n\n    code that\n    wraps\n"))))

(deftest table-is-ignored
  (is (= [] (flagged "| Name | Note |\n| ---- | ---- |\n| a    | no period |\n| b    | none |\n"))))

(deftest atx-and-setext-headings-are-ignored
  (is (= [] (flagged "# A heading\n\nA setext heading\nover two lines\n===\n"))))

(deftest html-block-is-ignored
  (is (= [] (flagged "<div>\nraw html that\nwraps\n</div>\n"))))

(deftest front-matter-is-ignored-and-line-numbers-still-match
  (is (= [8] (flagged "---\nname: x\ndescription: a value that\n\n  wraps\n---\n\nWrapped\nline.\n"))))

(deftest a-rule-that-is-not-front-matter-is-not-skipped
  (is (= [1] (flagged "Wrapped\nline.\n\n---\n"))))

;; Lists and block quotes

(deftest list-marker-lines-do-not-continue-the-paragraph-above
  (is (= [] (flagged "The lead-in\n- first item\n- second item\n"))))

(deftest tight-list-items-without-punctuation-pass
  (is (= [] (flagged "- one\n- two\n1. three\n2. four\n"))))

(deftest list-item-continuation-lines-are-checked
  (is (= [1] (flagged "- **Label.** A sentence that\n  wraps.\n  Next sentence.\n"))))

(deftest block-quote-lines-are-checked
  (is (= [1] (flagged "> A quote that\n> wraps.\n"))))

;; The command

(deftest a-clean-file-exits-0-and-prints-nothing
  (let [result (run (write "First sentence.\nSecond one.\n"))]
    (is (= [0 ""] [(:exit result) (:out result)]) (:err result))))

(deftest message-names-the-file-and-line
  (let [path (write "Wrapped\nline.\n")
        result (run path)]
    (is (= 1 (:exit result)) (:err result))
    (is (= (str path ":1: ends mid-sentence; break lines only between sentences\n") (:out result)))))

(deftest no-argument-is-a-usage-error
  (let [result (run)]
    (is (= 2 (:exit result)))
    (is (str/includes? (:err result) "Usage:"))))

(deftest help-prints-usage
  (let [result (run "--help")]
    (is (= 0 (:exit result)))
    (is (str/includes? (:out result) "Usage:"))))

(deftest missing-file-exits-2
  (let [result (run (str (fs/path *directory* "absent.md")))]
    (is (= 2 (:exit result)))
    (is (str/includes? (:err result) "absent.md"))))

(deftest reports-every-file
  (let [clean (write "Fine.\n" "clean.md")
        dirty (write "Not\nfine.\n" "dirty.md")
        result (run clean dirty)]
    (is (= 1 (:exit result)))
    (is (= [dirty] (map #(first (str/split % #":")) (str/split-lines (:out result)))))))
