#!/usr/bin/env bb
;; Flag Markdown paragraph lines that end mid-sentence.
;;
;; Why it exists: a Markdown file keeps one sentence per line, so a diff, a blame or a review
;; comment lands on one sentence, and no formatter splits sentences. This finds the lines that
;; break a sentence in two.
;;
;; Takes: Markdown files as arguments. A line is flagged when it sits inside a paragraph (in a
;; list item or a block quote too), another line of the same paragraph follows it, and it ends
;; without terminal punctuation (. ! ? or …, before any closing emphasis, code, bracket or quote
;; marks). Code blocks, tables, headings, HTML blocks, YAML front matter, the last line of each
;; paragraph, a line followed by a list item, and a line ending in a hard break (2 trailing
;; spaces or a backslash) are never flagged.
;;
;; The parser decides which lines are paragraph lines; each one's own text decides how it ends,
;; since cmark-gfm's positions for inlines go wrong after a backslash hard break.
;;
;;     markdown-sentence-per-line README.md docs/*.md
;;     bb scripts/sentence_per_line.clj README.md
;;
;; Prints `FILE:LINE: ...` for each flagged line. Exits 0 when nothing is flagged, 1 when a line
;; is, and 2 on a usage error or a file it can't read or parse.
;;
;; Parses with `cmark-gfm --sourcepos --to xml`, which must be on PATH, read through
;; clojure.data.xml.

(ns sentence-per-line
  (:require [babashka.process :as process]
            [clojure.data.xml :as xml]
            [clojure.string :as str]))

(def usage
  "Usage: markdown-sentence-per-line FILE...

Flag each Markdown paragraph line that ends mid-sentence, so every sentence sits on a line of
its own. Prints FILE:LINE for each one; exits 0 when none is found, 1 when one is, 2 on an
error.")

(def terminal-punctuation #{\. \! \? \… \。 \！ \？})

(def closing-marks #{\) \] \" \' \” \’ \» \* \_ \` \~ \space \tab})

(def front-matter-fences #{"---" "..."})

;; Pure core

(defn blank-front-matter
  "The text with a leading YAML front matter block's lines emptied, so line numbers still match
  the file and the parser reads no paragraph from it."
  [text]
  (let [lines (str/split-lines text)
        fence? #(contains? front-matter-fences (str/trimr %))
        close (when (and (seq lines) (= "---" (str/trimr (first lines))))
                (some #(when (fence? (nth lines %)) %) (range 1 (count lines))))]
    (if close
      (str/join "\n" (concat (repeat (inc close) "") (drop (inc close) lines)))
      text)))

(defn- node-name [node]
  (when (xml/element? node) (name (:tag node))))

(defn- line-span
  "The first and last lines of a node's `sourcepos` attribute, \"L:C-L:C\"."
  [node]
  (when-let [sourcepos (get-in node [:attrs :sourcepos])]
    (let [[start end] (str/split sourcepos #"-")]
      [(parse-long (first (str/split start #":")))
       (parse-long (first (str/split end #":")))])))

(defn hard-break?
  "Whether a source line ends in a hard line break: 2 or more spaces, or a backslash."
  [line]
  (or (str/ends-with? line "  ") (str/ends-with? line "\\")))

(defn ends-sentence?
  "Whether a source line's text ends with terminal punctuation, before any closing emphasis,
  code, bracket or quote marks."
  [line]
  (contains? terminal-punctuation
             (last (drop-last (count (take-while closing-marks (reverse line))) line))))

(defn- paragraphs [node]
  (filter #(= "paragraph" (node-name %)) (tree-seq xml/element? :content node)))

(defn flagged-lines
  "The sorted numbers of the lines that end mid-sentence: every line of a paragraph in the parsed
  document but its last, unless it ends a sentence or in a hard break. `lines` is the source the
  document was parsed from, split into lines."
  [document lines]
  (->> (paragraphs document)
       (keep line-span)
       (mapcat (fn [[start end]] (range start end)))
       (remove #(let [line (nth lines (dec %) "")]
                  (or (hard-break? line) (ends-sentence? line))))
       distinct
       sort))

(defn report-lines [path lines]
  (map #(str path ":" % ": ends mid-sentence; break lines only between sentences") lines))

;; Effectful shell

;; Compromise: plan node write-babashka-markdown-library, in github-config
(defn parse-markdown
  "The document tree of Markdown text, from cmark-gfm's XML with source positions."
  [text]
  (-> (process/shell {:in text :out :string}
                     "cmark-gfm" "--sourcepos" "--to" "xml"
                     "--extension" "table" "--extension" "strikethrough"
                     "--extension" "autolink" "--extension" "tasklist")
      :out
      (xml/parse-str :support-dtd false)))

(defn check-file [path]
  (try
    (let [text (blank-front-matter (slurp path))]
      {:path path
       :lines (flagged-lines (parse-markdown text) (str/split-lines text))})
    (catch Exception error
      {:path path :error (ex-message error)})))

(defn -main [& args]
  (cond
    (some #{"-h" "--help"} args) (do (println usage) 0)
    (empty? args) (do (binding [*out* *err*] (println usage)) 2)
    :else
    (let [results (mapv check-file args)]
      (doseq [{:keys [path lines error]} results]
        (if error
          (binding [*out* *err*] (println (str path ": " error)))
          (run! println (report-lines path lines))))
      (cond
        (some :error results) 2
        (some (comp seq :lines) results) 1
        :else 0))))

(when (= *file* (System/getProperty "babashka.file"))
  (System/exit (apply -main *command-line-args*)))
