document.addEventListener('DOMContentLoaded', () => {
    window.applyDiffHighlight = () => {
        const diffWrappers = document.querySelectorAll('.diff-wrapper');

        diffWrappers.forEach(wrapper => {
            const beforeContainer = wrapper.querySelector('.diff-container:nth-child(1) code');
            const afterContainer = wrapper.querySelector('.diff-container:nth-child(2) code');
            
            const diffData = wrapper.dataset.diff;

            if (!beforeContainer || !afterContainer || !diffData) {
                return;
            }

            try {
                const diffLines = JSON.parse(diffData);
                
                const beforeText = diffLines
                    .filter(line => !line.startsWith('+ '))
                    .map(line => line.substring(2))
                    .join('\n');

                const afterText = diffLines
                    .filter(line => !line.startsWith('- '))
                    .map(line => line.substring(2))
                    .join('\n');

                const dmp = new diff_match_patch();
                const diff = dmp.diff_main(beforeText, afterText);
                dmp.diff_cleanupSemantic(diff);

                beforeContainer.innerHTML = diffToHtml(diff, -1);
                afterContainer.innerHTML = diffToHtml(diff, 1);

            } catch (e) {
                console.error('Error processing diff data:', e);
                // В случае ошибки, просто показываем исходный код без подсветки diff
                const originalBefore = JSON.parse(wrapper.dataset.before);
                const originalAfter = JSON.parse(wrapper.dataset.after);
                beforeContainer.textContent = originalBefore;
                afterContainer.textContent = originalAfter;
            }
        });
    };

    function diffToHtml(diffs, type) {
        let html = '';
        for (const [op, data] of diffs) {
            const text = escapeHtml(data);
            if (op === 0) { // common
                html += text;
            } else if (op === type) { // insert or delete
                const className = type === 1 ? 'diff-add' : 'diff-sub';
                html += `<span class="${className}">${text}</span>`;
            }
        }
        return html;
    }

    function escapeHtml(text) {
        const map = {
            '&': '&',
            '<': '<',
            '>': '>',
            '"': '"',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, function(m) { return map[m]; });
    }
});